# Multilevel Feedback Queue (MLFQ) Scheduler Simulator

## Overview

This project implements a **Multilevel Feedback Queue (MLFQ) Scheduler** with a graphical user interface (GUI) built using PyQt6. The simulator demonstrates how operating systems schedule processes using multiple priority queues with different scheduling algorithms, aging mechanisms, and dynamic priority adjustments. 

## Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Queue Structure](#queue-structure)
- [Scheduling Algorithms](#scheduling-algorithms)
- [Installation](#installation)
- [Usage](#usage)
- [Parameters](#parameters)
- [Screenshots](#screenshots)
- [Technical Details](#technical-details)
- [Performance Metrics](#performance-metrics)

---

## Features

- **Four-Level Priority Queue System** with different scheduling algorithms per queue
- **Dynamic Priority Adjustment** through aging and demotion mechanisms
- **Multiple Scheduling Algorithms**:
  - First Come First Served (FCFS) - Queue 1
  - Shortest Job First (SJF) with optional preemption - Queue 2
  - Round Robin (RR) - Queues 3 & 4
- **Real-time Gantt Chart Visualization** of process execution
- **Comprehensive Process Statistics** including TAT, WT, and RT
- **Interactive GUI** for easy process management and parameter tuning
- **Optimized CPU Idle Handling** (jumps to next arrival time)

---

## System Architecture

The system consists of two main components:

### 1. **Scheduler Logic (`mlq_logic.py`)**
- Core scheduling algorithm implementation
- Queue management and process state tracking
- Statistics calculation and event generation

### 2. **GUI Application (`gui_app.py`)**
- User interface for process input and parameter configuration
- Real-time simulation output display
- Gantt chart visualization using Matplotlib
- Statistical analysis presentation

![System Architecture Diagram]
*[Screenshot Placeholder: Add system architecture or component diagram here]*

---

## Queue Structure

The scheduler uses **4 priority queues**, numbered from highest (1) to lowest (4) priority:

| Queue | Priority | Algorithm | Preemption | Use Case |
|-------|----------|-----------|------------|----------|
| **Q1** | Highest | FCFS | No | Short, interactive processes |
| **Q2** | High | SJF (Preemptive) | Optional | I/O bound processes |
| **Q3** | Low | Round Robin | Yes (Quantum) | CPU-bound processes |
| **Q4** | Lowest | Round Robin | Yes (Quantum) | Background/batch jobs |

![Queue Structure Diagram]
*[Screenshot Placeholder: Add queue hierarchy visualization here]*

---

## Scheduling Algorithms

### Queue 1: First Come First Served (FCFS)
- Processes execute in **arrival order**
- **Non-preemptive** - runs to completion
- Ideal for short, high-priority tasks

### Queue 2: Shortest Job First (SJF)
- Selects process with **shortest remaining burst time**
- **Optional preemption** when shorter job arrives
- Minimizes average waiting time
- Toggle preemption via GUI checkbox

### Queues 3 & 4: Round Robin (RR)
- Each process gets a **time quantum**
- **Preemptive** - switches after quantum expires
- Fair CPU time distribution
- Prevents process starvation

---

## Installation

### Prerequisites

```bash
Python 3.8 or higher
PyQt6
Matplotlib
```

### Install Dependencies

```bash
pip install PyQt6 matplotlib
```

### File Structure

```
project/
│
├── mlq_logic.py          # Core scheduler logic
├── gui_app.py            # GUI application
└── README.md             # This file
```

---

## Usage

### Running the Simulator

```bash
python gui_app.py
```

### Step-by-Step Guide

1. **Launch Application**
   - Run `gui_app.py`
   - Default processes are pre-loaded

2. **Manage Processes**
   - Click **"Add Process"** to add new processes
   - Click **"Remove Selected"** to delete a process
   - Edit cells directly in the table (Arrival, Burst, Priority)

3. **Configure Parameters**
   - **Time Quantum**: CPU time slice for Round Robin (default: 3)
   - **Aging Threshold**: Wait time before priority promotion (default: 5)
   - **Demotion Threshold**: Process time before priority demotion (default: 6)
   - **Preemptive SJF**: Enable/disable preemption in Queue 2

4. **Run Simulation**
   - Click **"Run Simulation"**
   - View real-time execution log
   - Analyze Gantt chart
   - Review process statistics

5. **Reset to Default**
   - Click **"Reset to Default"** to restore default configuration

![Main Application Window]
*[Screenshot Placeholder: Add main GUI window screenshot here]*

---

## Parameters

### Input Parameters

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| **Arrival Time** | When process arrives at system | 0+ | Varies |
| **Burst Time** | Total CPU time required | 1+ | Varies |
| **Priority** | Initial queue assignment | 1-4 | Varies |
| **Time Quantum** | RR time slice duration | 1-20 | 3 |
| **Aging Threshold** | Wait time for promotion | 1-20 | 5 |
| **Demotion Threshold** | Execution time for demotion | 1-20 | 6 |

### Default Process Set

| Process | Arrival | Burst | Priority |
|---------|---------|-------|----------|
| P1 | 1 | 20 | 3 |
| P2 | 3 | 10 | 2 |
| P3 | 5 | 2 | 1 |
| P4 | 8 | 7 | 2 |
| P5 | 11 | 15 | 3 |
| P6 | 15 | 8 | 2 |
| P7 | 20 | 4 | 1 |

---

## Screenshots

### Main Interface

![Main Interface]
*[Screenshot Placeholder: Add main interface with process table and parameters]*

### Simulation Output

![Simulation Output]
*[Screenshot Placeholder: Add simulation output log with color-coded events]*

### Gantt Chart

![Gantt Chart]
*[Screenshot Placeholder: Add Gantt chart showing process execution timeline]*

### Process Statistics

![Statistics Table]
*[Screenshot Placeholder: Add statistics table with TAT, WT, RT calculations]*

### Aging Mechanism

![Aging Example]
*[Screenshot Placeholder: Add screenshot showing aging promotion events]*

### Preemption in Action

![Preemption]
*[Screenshot Placeholder: Add screenshot showing SJF preemption event]*

---

## Technical Details

### Dynamic Priority Adjustments

#### **Aging (Priority Promotion)**
- Prevents process starvation
- When wait time ≥ aging threshold
- Process moves to higher priority queue (Q4→Q3→Q2→Q1)
- Wait time resets to 0
- Example: Process waits 5+ time units → promoted

#### **Demotion (Priority Demotion)**
- Penalizes CPU-intensive processes
- Only applies to Q3 and Q4 (Round Robin queues)
- When process time ≥ demotion threshold
- Process moves to lower priority queue (Q3→Q4)
- Process time resets to 0
- Example: Process uses CPU for 6+ time units → demoted

![Priority Adjustment Flow]
*[Screenshot Placeholder: Add flowchart of aging/demotion mechanism]*

### Event Order in Main Loop

The scheduler processes events in this order each time unit:

1. **Process Arrivals** - Add newly arrived processes to queues
2. **Update Waiting Times** - Calculate time spent waiting
3. **Apply Aging** - Promote starving processes
4. **Select Next Process** - Choose from highest priority queue
5. **Execute Process** - Run for quantum or to completion
6. **Handle Preemption/Completion** - Demote, re-queue, or complete

### CPU Idle Optimization

When no processes are ready:
- **Old Behavior**: Increment time by 1 unit
- **New Behavior**: Jump directly to next arrival time
- **Benefit**: Dramatically faster simulation with sparse arrivals

```python
# Example: Time 10, next arrival at time 25
# Skips times 11-24 instantly
```

---

## Performance Metrics

### Calculated Statistics

For each process, the simulator calculates:

| Metric | Formula | Description |
|--------|---------|-------------|
| **AT** | User Input | Arrival Time |
| **BT** | User Input | Burst Time (total CPU needed) |
| **CT** | Simulation Result | Completion Time |
| **TAT** | CT - AT | Turnaround Time (total time in system) |
| **WT** | Accumulated Wait | Waiting Time (time spent waiting) |
| **RT** | First_Run - AT | Response Time (time to first execution) |

### Average Metrics

The system calculates averages across all processes:
- **Average Turnaround Time (Avg TAT)**
- **Average Waiting Time (Avg WT)**
- **Average Response Time (Avg RT)**

These metrics help evaluate scheduler performance and fairness.

![Statistics Example]
*[Screenshot Placeholder: Add detailed statistics output with calculations]*

---

## Algorithm Comparison

### FCFS (Queue 1)
**Advantages:**
- Simple, fair ordering
- No starvation
- Low overhead

**Disadvantages:**
- Convoy effect (short jobs wait for long jobs)
- Poor average waiting time

### SJF (Queue 2)
**Advantages:**
- Optimal average waiting time
- Good for I/O bound processes
- Preemption option for fairness

**Disadvantages:**
- Can cause starvation (mitigated by aging)
- Requires burst time estimation

### Round Robin (Queues 3 & 4)
**Advantages:**
- Fair time distribution
- Good for time-sharing
- Responsive for interactive processes

**Disadvantages:**
- Context switching overhead
- Higher average turnaround time
- Quantum selection critical

![Algorithm Comparison Chart]
*[Screenshot Placeholder: Add bar chart comparing average times across algorithms]*

---

## Example Simulation

### Sample Run Output

```
ARRIVAL: P1 arrived at TIME 1 → added to Q3
TIME 2: RUN P1 | Remaining=19 | Q=3 (RR) | PT=1
ARRIVAL: P2 arrived at TIME 3 → added to Q2
TIME 4: RUN P1 | Remaining=18 | Q=3 (RR) | PT=2
AGING: P2 promoted from Q2 → Q1
PREEMPTION: P1 preempted in Q2 (shorter job arrived)
TIME 5: RUN P2 | Remaining=9 | Q=1 (FCFS) | PT=1
...
PROCESS P3 completed at TIME 25
```

### Color Coding

- 🟢 **Green**: Process completion
- 🔵 **Blue**: Aging (promotion)
- 🟠 **Orange**: Demotion
- 🔴 **Red**: Preemption
- ⚪ **Gray**: CPU idle

---

## Troubleshooting

### Common Issues

**Issue**: GUI doesn't launch
- **Solution**: Ensure PyQt6 is installed: `pip install PyQt6`

**Issue**: Gantt chart doesn't appear
- **Solution**: Install Matplotlib: `pip install matplotlib`

**Issue**: Process statistics show incorrect values
- **Solution**: Check that arrival times are sequential and burst times are positive

**Issue**: Simulation hangs
- **Solution**: Verify all processes have valid burst times (> 0)

---

## Future Enhancements

Possible improvements for future versions:

- [ ] Multi-core/multi-processor simulation
- [ ] I/O burst modeling
- [ ] Priority inheritance for synchronization
- [ ] Real-time process constraints
- [ ] Save/load configuration files
- [ ] Export statistics to CSV
- [ ] Animation of queue transitions
- [ ] Compare multiple scheduling policies side-by-side

---

## References

### Academic Resources

1. **Operating System Concepts** (Silberschatz, Galvin, Gagne)
   - Chapter 5: CPU Scheduling

2. **Modern Operating Systems** (Andrew S. Tanenbaum)
   - Section 2.4: Scheduling

3. **Operating Systems: Three Easy Pieces** (Remzi H. Arpaci-Dusseau)
   - Chapter: Multi-Level Feedback Queue

### Online Resources

- [MLFQ Scheduling Algorithm](https://en.wikipedia.org/wiki/Multilevel_feedback_queue)
- [CPU Scheduling Algorithms](https://www.geeksforgeeks.org/cpu-scheduling-in-operating-systems/)

---

## License

This project is created for educational purposes.

---

## Authors

**Operating Systems Course Project**

Redzer Riley Monsod
Roy Garcia 
Keyro Sibug

---

## Acknowledgments

- PyQt6 for the GUI framework
- Matplotlib for visualization
- Operating Systems course materials and references

---

**Last Updated**: 2025

**Version**: 1.0.0
