from collections import deque

def run_scheduler(processes, quantum=3, aging_threshold=5, demotion_threshold=6, preemptive_sjf=True):
    queues = {1: deque(), 2: deque(), 3: deque(), 4: deque()}
    remaining = {p["id"]: p["burst"] for p in processes}
    priority = {p["id"]: p["priority"] for p in processes}
    proc_time = {p["id"]: 0 for p in processes}
    wait_time = {p["id"]: 0 for p in processes}
    queue_entry_time = {p["id"]: -1 for p in processes}
    completed = set()
    
    # Track statistics
    stats = {
        p["id"]: {
            "arrival_time": p["arrival"],
            "burst_time": p["burst"],
            "first_response_time": None,
            "completion_time": None,
            "total_waiting_time": 0,
            "last_wait_start": None
        }
        for p in processes
    }

    time = 0

    def enqueue(pid, qid, reset_proc_time=False, reset_wait_time=False):
        if pid not in queues[qid]:
            queues[qid].append(pid)
        priority[pid] = qid
        if reset_proc_time:
            proc_time[pid] = 0
        if reset_wait_time:
            wait_time[pid] = 0
            queue_entry_time[pid] = time
        # Always reset last_wait_start when entering queue
        stats[pid]["last_wait_start"] = time

    def update_waiting(running_pid=None):
        for p in processes:
            pid = p["id"]
            if pid not in completed and pid != running_pid:
                is_queued = any(pid in q for q in queues.values())
                if is_queued and queue_entry_time[pid] != -1:
                    wait_time[pid] = time - queue_entry_time[pid]

    def apply_aging():
        promoted = []
        for qid in [2, 3, 4]:
            for pid in list(queues[qid]):
                if wait_time[pid] >= aging_threshold and qid > 1:
                    promoted.append((pid, qid))
        
        for pid, old_qid in promoted:
            for qid in [1, 2, 3, 4]:
                if pid in queues[qid]:
                    queues[qid].remove(pid)
            new_qid = old_qid - 1
            queues[new_qid].append(pid)
            priority[pid] = new_qid
            wait_time[pid] = 0
            queue_entry_time[pid] = time
            stats[pid]["last_wait_start"] = time
            yield f"AGING: {pid} promoted from Q{old_qid} → Q{new_qid}"

    def add_arrivals():
        for p in processes:
            if p["arrival"] == time:
                queue_entry_time[p["id"]] = time
                enqueue(p["id"], p["priority"], reset_proc_time=True, reset_wait_time=True)
                yield f"ARRIVAL: {p['id']} arrived at TIME {time} → added to Q{p['priority']}"

    def get_next_arrival_time():
        """Get the time of the next process arrival after current time"""
        future_arrivals = [p["arrival"] for p in processes if p["arrival"] > time and p["id"] not in completed]
        return min(future_arrivals) if future_arrivals else None

    def get_highest_priority_queue():
        for qid in [1, 2, 3, 4]:
            if queues[qid]:
                return qid
        return None

    def get_next_process(qid):
        """Get next process based on queue algorithm"""
        if qid == 1:
            # FCFS: First process in queue
            return queues[qid].popleft()
        elif qid == 2:
            # SJF: Process with shortest remaining burst time
            shortest_pid = min(queues[qid], key=lambda pid: remaining[pid])
            queues[qid].remove(shortest_pid)
            return shortest_pid
        else:
            # Round Robin for Q3 and Q4
            return queues[qid].popleft()

    def start_execution(pid):
        """Called when process starts executing"""
        if stats[pid]["first_response_time"] is None:
            stats[pid]["first_response_time"] = time
        # Add accumulated waiting time
        if stats[pid]["last_wait_start"] is not None:
            stats[pid]["total_waiting_time"] += (time - stats[pid]["last_wait_start"])
            stats[pid]["last_wait_start"] = None

    def pause_execution(pid):
        """Called when process is paused (preempted)"""
        stats[pid]["last_wait_start"] = time

    def should_preempt_sjf(current_pid, current_q):
        """Check if a newly arrived process should preempt current SJF process"""
        if not preemptive_sjf or current_q != 2:
            return False
        # Check if there's a shorter job in Q2
        if queues[2]:
            shortest_in_queue = min(queues[2], key=lambda pid: remaining[pid])
            return remaining[shortest_in_queue] < remaining[current_pid]
        return False

    while len(completed) < len(processes):
        # FIRST: Process arrivals
        yield from add_arrivals()
        
        # SECOND: Update waiting times
        update_waiting()
        
        # THIRD: Apply aging
        yield from apply_aging()

        current_q = get_highest_priority_queue()
        if not current_q:
            # Optimize: Jump to next arrival time instead of incrementing by 1
            next_arrival = get_next_arrival_time()
            if next_arrival is not None:
                yield f"TIME {time}: CPU IDLE → jumping to TIME {next_arrival}"
                time = next_arrival
            else:
                yield f"TIME {time}: CPU IDLE (no more processes)"
                time += 1
            continue

        pid = get_next_process(current_q)
        start_execution(pid)
        used_time = 0

        # Queue 1 (FCFS): Run to completion
        # Queue 2 (SJF): Run to completion (or preemptive if enabled)
        # Queue 3 & 4 (RR): Use quantum
        if current_q in [1, 2]:
            # Run to completion for FCFS and SJF (with optional preemption for SJF)
            while remaining[pid] > 0:
                remaining[pid] -= 1
                proc_time[pid] += 1
                used_time += 1
                time += 1

                # FIRST: Process arrivals
                yield from add_arrivals()
                
                # SECOND: Update waiting times
                update_waiting(running_pid=pid)
                
                # THIRD: Apply aging
                yield from apply_aging()

                algo = "FCFS" if current_q == 1 else ("SJF-P" if preemptive_sjf else "SJF")
                yield f"TIME {time}: RUN {pid} | Remaining={remaining[pid]} | Q{current_q} ({algo}) | PT={proc_time[pid]}"

                # Check for preemption in SJF
                if should_preempt_sjf(pid, current_q):
                    pause_execution(pid)
                    queues[current_q].append(pid)
                    wait_time[pid] = 0
                    queue_entry_time[pid] = time
                    yield f"PREEMPTION: {pid} preempted in Q{current_q} (shorter job arrived)"
                    break

                if remaining[pid] == 0:
                    break
        else:
            # Round Robin for Q3 and Q4
            while remaining[pid] > 0 and used_time < quantum:
                remaining[pid] -= 1
                proc_time[pid] += 1
                used_time += 1
                time += 1

                # FIRST: Process arrivals
                yield from add_arrivals()
                
                # SECOND: Update waiting times
                update_waiting(running_pid=pid)
                
                # THIRD: Apply aging
                yield from apply_aging()

                yield f"TIME {time}: RUN {pid} | Remaining={remaining[pid]} | Q={current_q} (RR) | PT={proc_time[pid]}"

                if remaining[pid] == 0:
                    break

        if remaining[pid] == 0:
            completed.add(pid)
            stats[pid]["completion_time"] = time
            wait_time[pid] = 0
            proc_time[pid] = 0
            queue_entry_time[pid] = -1
            yield f"PROCESS {pid} completed at TIME {time}"
        elif current_q >= 3 and used_time >= quantum:
            # Only Q3 and Q4 use quantum and can be demoted
            pause_execution(pid)
            if proc_time[pid] >= demotion_threshold and current_q < 4:
                new_q = current_q + 1
                queues[new_q].append(pid)
                priority[pid] = new_q
                proc_time[pid] = 0
                wait_time[pid] = 0
                queue_entry_time[pid] = time
                yield f"DEMOTION: {pid} demoted from Q{current_q} → Q{new_q} (PT reached {demotion_threshold})"
            else:
                # Finished quantum but not demoted → back to end of same queue
                queues[current_q].append(pid)
                wait_time[pid] = 0
                queue_entry_time[pid] = time
                yield f"{pid} quantum expired → back to Q{current_q}"
    
    # Calculate final statistics
    for pid, s in stats.items():
        if s["completion_time"] is not None:
            s["turnaround_time"] = s["completion_time"] - s["arrival_time"]
            s["waiting_time"] = s["total_waiting_time"]
            s["response_time"] = s["first_response_time"] - s["arrival_time"] if s["first_response_time"] else 0
    
    # Return statistics at the end
    yield ("STATS", stats)