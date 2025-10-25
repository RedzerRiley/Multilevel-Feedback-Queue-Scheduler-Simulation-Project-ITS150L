from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QLabel, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from mlq_logic import run_scheduler
import matplotlib.pyplot as plt


class SchedulerGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multilevel Feedback Queue Scheduler")
        self.resize(900, 650)

        layout = QVBoxLayout()

        # Process table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Arrival", "Burst", "Priority"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

        layout.addWidget(QLabel("Process Table:"))
        layout.addWidget(self.table)

        # Scheduler parameter controls
        param_layout = QHBoxLayout()

        self.quantum_input = QSpinBox()
        self.quantum_input.setRange(1, 20)
        self.quantum_input.setValue(3)
        param_layout.addWidget(QLabel("Time Quantum:"))
        param_layout.addWidget(self.quantum_input)

        self.aging_input = QSpinBox()
        self.aging_input.setRange(1, 20)
        self.aging_input.setValue(5)
        param_layout.addWidget(QLabel("Aging (Increase Priority):"))
        param_layout.addWidget(self.aging_input)

        self.demotion_input = QSpinBox()
        self.demotion_input.setRange(1, 20)
        self.demotion_input.setValue(6)
        param_layout.addWidget(QLabel("Demotion (Decrease Priority):"))
        param_layout.addWidget(self.demotion_input)

        layout.addLayout(param_layout)
        
        # Add preemptive SJF checkbox
        from PyQt6.QtWidgets import QCheckBox
        preempt_layout = QHBoxLayout()
        self.preemptive_sjf_checkbox = QCheckBox("Enable Preemptive SJF (Queue 2)")
        self.preemptive_sjf_checkbox.setChecked(True)
        preempt_layout.addWidget(self.preemptive_sjf_checkbox)
        preempt_layout.addStretch()
        layout.addLayout(preempt_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Process")
        self.add_button.clicked.connect(self.add_process)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_process)
        button_layout.addWidget(self.remove_button)

        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(self.reset_button)

        self.run_button = QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.run_simulation)
        button_layout.addWidget(self.run_button)

        layout.addLayout(button_layout)

        # Output box
        layout.addWidget(QLabel("Simulation Output:"))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

        # Load defaults at startup
        self.reset_to_default()

    def load_default_processes(self):
        """Returns the default process list"""
        return [
            {"id": "P1", "arrival": 1, "burst": 20, "priority": 3},
            {"id": "P2", "arrival": 3, "burst": 10, "priority": 2},
            {"id": "P3", "arrival": 5, "burst": 2, "priority": 1},
            {"id": "P4", "arrival": 8, "burst": 7, "priority": 2},
            {"id": "P5", "arrival": 11, "burst": 15, "priority": 3},
            {"id": "P6", "arrival": 15, "burst": 8, "priority": 2},
            {"id": "P7", "arrival": 20, "burst": 4, "priority": 1},
        ]

    def reset_to_default(self):
        """Reset table and parameters to default values"""
        self.table.setRowCount(0)
        for p in self.load_default_processes():
            self.add_process(p["arrival"], p["burst"], p["priority"])

        self.quantum_input.setValue(3)
        self.aging_input.setValue(5)
        self.demotion_input.setValue(6)

        self.output.clear()

    def add_process(self, arrival=0, burst=1, priority=1):
        row = self.table.rowCount()
        self.table.insertRow(row)
        pid = f"P{row+1}"
        self.table.setVerticalHeaderItem(row, QTableWidgetItem(pid))
        self.table.setItem(row, 0, QTableWidgetItem(str(arrival)))
        self.table.setItem(row, 1, QTableWidgetItem(str(burst)))
        self.table.setItem(row, 2, QTableWidgetItem(str(priority)))

    def remove_process(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)
            for row in range(self.table.rowCount()):
                self.table.setVerticalHeaderItem(row, QTableWidgetItem(f"P{row+1}"))

    def get_processes_from_table(self):
        processes = []
        for row in range(self.table.rowCount()):
            pid = f"P{row+1}"
            arrival = int(self.table.item(row, 0).text())
            burst = int(self.table.item(row, 1).text())
            priority = int(self.table.item(row, 2).text())
            processes.append({"id": pid, "arrival": arrival, "burst": burst, "priority": priority})
        return processes

    def run_simulation(self):
        self.output.clear()
        self.output.append("<b><font color='blue'>Simulation started...</font></b><br>")
        self.gantt_data = []

        processes = self.get_processes_from_table()
        quantum = self.quantum_input.value()
        aging_threshold = self.aging_input.value()
        demotion_threshold = self.demotion_input.value()

        stats = None

        try:
            for step in run_scheduler(processes, quantum, aging_threshold, demotion_threshold):
                # Check if this is the statistics tuple
                if isinstance(step, tuple) and step[0] == "STATS":
                    stats = step[1]
                    continue
                
                self.output.append(self.colorize(step))
                
                if step.startswith("TIME") and "RUN" in step:
                    parts = step.split()
                    time = int(parts[1].replace(":", ""))
                    pid = parts[3]
                    self.gantt_data.append((time, pid))

            if stats:
                self.show_gantt_chart()
                self.show_statistics(stats)

        except Exception as e:
            self.output.append(f"<b><font color='red'>[ERROR]</font></b> {e}")

    def colorize(self, text: str) -> str:
        if "completed" in text:
            return f"<font color='green'><b>{text}</b></font>"
        elif "DEMOTION" in text:
            return f"<font color='orange'><b>{text}</b></font>"
        elif "AGING" in text:
            return f"<font color='blue'><b>{text}</b></font>"
        elif "IDLE" in text.lower():
            return f"<font color='gray'>{text}</font>"
        else:
            return text

    def show_gantt_chart(self):
        if not self.gantt_data:
            return

        fig, ax = plt.subplots(figsize=(10, 4))
        colors = {}
        for t, pid in self.gantt_data:
            if pid not in colors:
                colors[pid] = plt.cm.tab10(len(colors) % 10)
            ax.barh(y=pid, width=1, left=t, color=colors[pid], edgecolor="black", linewidth=0.5)

        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Process", fontsize=12)
        ax.set_title("Gantt Chart - Process Execution Timeline", fontsize=14, fontweight='bold')
        ax.set_yticks([p for p in sorted(set(pid for _, pid in self.gantt_data))])
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        min_time = min(t for t, _ in self.gantt_data)
        max_time = max(t for t, _ in self.gantt_data)
        ax.set_xlim(min_time - 0.5, max_time + 0.5)
        
        plt.tight_layout()
        plt.show()

    def show_statistics(self, stats):
        self.output.append("<br><b><font color='purple'>╔════════════════════════════════════════════════════════════╗</font></b>")
        self.output.append("<b><font color='purple'>║          PROCESS SCHEDULING STATISTICS                     ║</font></b>")
        self.output.append("<b><font color='purple'>╚════════════════════════════════════════════════════════════╝</font></b><br>")
        
        # Create a formatted table header
        header = (
            "<b><font color='darkblue'>"
            f"{'Process':<10} {'AT':<6} {'BT':<6} {'CT':<6} {'TAT':<6} {'WT':<6} {'RT':<6}"
            "</font></b>"
        )
        self.output.append(header)
        self.output.append("<font color='gray'>─────────────────────────────────────────────────────────</font>")
        
        total_tat = 0
        total_wt = 0
        total_rt = 0
        process_count = 0
        
        for pid in sorted(stats.keys()):
            s = stats[pid]
            
            if s["completion_time"] is None:
                continue
            
            at = s["arrival_time"]
            bt = s["burst_time"]
            ct = s["completion_time"]
            rt = s["first_response_time"] - at if s["first_response_time"] is not None else 0
            tat = ct - at
            wt = s["total_waiting_time"]
            
            total_tat += tat
            total_wt += wt
            total_rt += rt
            process_count += 1
            
            row = (
                f"<font color='darkgreen'>{pid:<10}</font> "
                f"{at:<6} {bt:<6} {ct:<6} "
                f"<font color='teal'>{tat:<6}</font> "
                f"<font color='brown'>{wt:<6}</font> "
                f"<font color='navy'>{rt:<6}</font>"
            )
            self.output.append(row)
        
        # Add separator
        self.output.append("<font color='gray'>─────────────────────────────────────────────────────────</font>")
        
        # Calculate averages
        if process_count > 0:
            avg_tat = total_tat / process_count
            avg_wt = total_wt / process_count
            avg_rt = total_rt / process_count
            
            self.output.append("<br><b><font color='purple'>AVERAGE TIMES:</font></b>")
            self.output.append(f"<font color='teal'>• Average Turnaround Time (TAT): {avg_tat:.2f}</font>")
            self.output.append(f"<font color='brown'>• Average Waiting Time (WT):     {avg_wt:.2f}</font>")
            self.output.append(f"<font color='navy'>• Average Response Time (RT):    {avg_rt:.2f}</font>")
        
        self.output.append("<br><b><font color='gray'>Legend:</font></b>")
        self.output.append("<font color='gray'>AT = Arrival Time | BT = Burst Time | CT = Completion Time</font>")
        self.output.append("<font color='gray'>TAT = Turnaround Time | WT = Waiting Time | RT = Response Time</font>")


if __name__ == "__main__":
    app = QApplication([])
    window = SchedulerGUI()
    window.show()
    app.exec()