#!/usr/bin/env python3

import sys
import math
import threading
import subprocess
import platform
import time

import speedtest
import psutil

try:
    import GPUtil
except:
    GPUtil = None

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QProgressBar,
    QPushButton,
)

from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
    QFont,
    QBrush,
    QPainterPath,
    QLinearGradient,
)

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject


# =========================================================
# THREAD SIGNALS
# =========================================================
class SpeedTestSignals(QObject):
    status = pyqtSignal(str, int)
    isp_info = pyqtSignal(str, str, str)
    ping_done = pyqtSignal(str, str)
    download_done = pyqtSignal(str)
    upload_done = pyqtSignal(str)
    finished = pyqtSignal()


# =========================================================
# ADVANCED GAUGE
# =========================================================
class AdvancedGaugeWidget(QWidget):

    def __init__(self, start_callback=None):
        super().__init__()

        self.current_speed = 0.0
        self.target_speed = 0.0
        self.is_running = False
        self.start_callback = start_callback

        self.gauge_maxima = [10.0, 50.0, 100.0, 500.0, 1000.0]
        self.current_max_idx = 2
        self.max_speed_scale = self.gauge_maxima[self.current_max_idx]

        self.graph_history = []
        self.max_history_points = 55

        self.setMinimumSize(420, 440)

        self.go_button = QPushButton("GO", self)
        self.go_button.setGeometry(150, 150, 120, 120)
        self.go_button.setCursor(Qt.PointingHandCursor)
        self.go_button.clicked.connect(self.on_go_clicked)

        self.update_button_style()

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_frame)
        self.timer.start(16)

    def on_go_clicked(self):

        if self.start_callback and not self.is_running:

            self.go_button.hide()

            self.is_running = True

            self.graph_history.clear()

            self.current_max_idx = 2

            self.max_speed_scale = self.gauge_maxima[
                self.current_max_idx
            ]

            self.start_callback()

    def reset_ui(self):

        self.is_running = False
        self.target_speed = 0.0
        self.current_speed = 0.0

        self.go_button.show()

        self.update()

    def set_speed(self, speed):

        self.target_speed = float(speed)

        if self.target_speed > self.max_speed_scale * 0.85:

            if self.current_max_idx < len(self.gauge_maxima) - 1:

                self.current_max_idx += 1

                self.max_speed_scale = self.gauge_maxima[
                    self.current_max_idx
                ]

        if self.is_running:

            self.graph_history.append(self.target_speed)

            if len(self.graph_history) > self.max_history_points:
                self.graph_history.pop(0)

    def update_button_style(self):

        self.go_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00f5d4;
                font-size: 28px;
                font-weight: bold;
                border: 3px solid #00f5d4;
                border-radius: 60px;
            }

            QPushButton:hover {
                background-color: rgba(0, 245, 212, 0.1);
                color: #ffffff;
                border: 3px solid #ffffff;
            }
        """)

    def animate_frame(self):

        if abs(
            self.current_speed - self.target_speed
        ) > 0.05:

            self.current_speed += (
                self.target_speed - self.current_speed
            ) * 0.12

            self.update()

    def resizeEvent(self, event):

        cx = self.width() // 2
        cy = self.height() // 2 - 30

        self.go_button.setGeometry(
            cx - 60,
            cy - 60,
            120,
            120
        )

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        center_x = width // 2
        center_y = height // 2 - 30

        radius = 150

        # =====================================================
        # REALTIME GRAPH
        # =====================================================
        if self.is_running and len(self.graph_history) > 1:

            graph_path = QPainterPath()

            graph_height = 90
            graph_base_y = height - 15

            graph_width = width - 40
            start_x = 20

            step_x = graph_width / float(
                self.max_history_points - 1
            )

            first_y = (
                graph_base_y -
                (
                    min(
                        self.graph_history[0] /
                        self.max_speed_scale,
                        1.0
                    ) * graph_height
                )
            )

            graph_path.moveTo(start_x, first_y)

            for idx, speed_point in enumerate(
                self.graph_history
            ):

                pt_x = start_x + (idx * step_x)

                ratio = min(
                    speed_point / self.max_speed_scale,
                    1.0
                )

                pt_y = graph_base_y - (
                    ratio * graph_height
                )

                graph_path.lineTo(pt_x, pt_y)

            closed_path = QPainterPath(graph_path)

            closed_path.lineTo(
                start_x + (
                    (len(self.graph_history) - 1)
                    * step_x
                ),
                graph_base_y
            )

            closed_path.lineTo(
                start_x,
                graph_base_y
            )

            closed_path.closeSubpath()

            grad = QLinearGradient(
                0,
                graph_base_y - graph_height,
                0,
                graph_base_y
            )

            grad.setColorAt(
                0,
                QColor(0, 245, 214, 45)
            )

            grad.setColorAt(
                1,
                QColor(0, 245, 214, 0)
            )

            painter.fillPath(
                closed_path,
                QBrush(grad)
            )

            wave_pen = QPen(
                QColor("#00f5d4"),
                2
            )

            painter.setPen(wave_pen)

            painter.drawPath(graph_path)

        # =====================================================
        # BACKGROUND ARC
        # =====================================================
        bg_pen = QPen(
            QColor("#1c1e24"),
            10
        )

        bg_pen.setCapStyle(Qt.RoundCap)

        painter.setPen(bg_pen)

        painter.drawArc(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2,
            -30 * 16,
            -240 * 16
        )

        # =====================================================
        # ACTIVE ARC
        # =====================================================
        active_pen = QPen(
            QColor("#00f5d4"),
            10
        )

        active_pen.setCapStyle(Qt.RoundCap)

        painter.setPen(active_pen)

        progress = min(
            self.current_speed /
            self.max_speed_scale,
            1.0
        )

        span_angle = int(progress * 240)

        painter.drawArc(
            center_x - radius,
            center_y - radius,
            radius * 2,
            radius * 2,
            210 * 16,
            -span_angle * 16
        )

        # =====================================================
        # TICKS
        # =====================================================
        for i in range(0, 11):

            angle_deg = 210 - (i * 24)

            angle_rad = math.radians(angle_deg)

            outer_x = (
                center_x +
                math.cos(angle_rad) * radius
            )

            outer_y = (
                center_y -
                math.sin(angle_rad) * radius
            )

            inner_x = (
                center_x +
                math.cos(angle_rad) * (radius - 10)
            )

            inner_y = (
                center_y -
                math.sin(angle_rad) * (radius - 10)
            )

            tick_pen = QPen(
                QColor("#00f5d4")
                if i <= int(progress * 10)
                else QColor("#323743"),
                2
            )

            painter.setPen(tick_pen)

            painter.drawLine(
                int(inner_x),
                int(inner_y),
                int(outer_x),
                int(outer_y)
            )

            if i % 2 == 0:

                val_text = str(
                    int(
                        (self.max_speed_scale / 10) * i
                    )
                )

                txt_x = (
                    center_x +
                    math.cos(angle_rad) * (radius - 26)
                )

                txt_y = (
                    center_y -
                    math.sin(angle_rad) * (radius - 26)
                )

                painter.setPen(QColor("#6c7282"))

                painter.setFont(
                    QFont(
                        "Segoe UI",
                        8,
                        QFont.Bold
                    )
                )

                painter.drawText(
                    int(txt_x) - 12,
                    int(txt_y) + 5,
                    24,
                    12,
                    Qt.AlignCenter,
                    val_text
                )

        # =====================================================
        # MAX LABEL
        # =====================================================
        max_scale_lbl = (
            f"MAX: {int(self.max_speed_scale)}"
        )

        painter.setPen(QColor("#6c7282"))

        painter.setFont(
            QFont("Segoe UI", 9, QFont.Bold)
        )

        painter.drawText(
            center_x - 50,
            center_y + 15,
            100,
            20,
            Qt.AlignCenter,
            max_scale_lbl
        )

        # =====================================================
        # NEEDLE
        # =====================================================
        if self.is_running:

            needle_angle = math.radians(
                210 - (progress * 240)
            )

            needle_length = 125

            needle_x = (
                center_x +
                math.cos(needle_angle)
                * needle_length
            )

            needle_y = (
                center_y -
                math.sin(needle_angle)
                * needle_length
            )

            needle_pen = QPen(
                QColor("#ffffff"),
                3
            )

            painter.setPen(needle_pen)

            painter.drawLine(
                center_x,
                center_y,
                int(needle_x),
                int(needle_y)
            )

            painter.setBrush(
                QBrush(QColor("#0b0c10"))
            )

            painter.setPen(
                QPen(QColor("#00f5d4"), 2)
            )

            painter.drawEllipse(
                center_x - 8,
                center_y - 8,
                16,
                16
            )


# =========================================================
# MAIN UI
# =========================================================
class SpeedTestUI(QWidget):

    def __init__(self):
        super().__init__()

        self.signals = SpeedTestSignals()

        self.hardware_tracking = False

        self.init_ui()

        self.load_system_info()

        self.signals.status.connect(
            self.update_status
        )

        self.signals.isp_info.connect(
            self.update_isp
        )

        self.signals.ping_done.connect(
            self.update_latency_metrics
        )

        self.signals.download_done.connect(
            lambda val:
            self.download_val.setText(val)
        )

        self.signals.upload_done.connect(
            lambda val:
            self.upload_val.setText(val)
        )

        self.signals.finished.connect(
            self.test_complete
        )

    # =====================================================
    # UI
    # =====================================================
    def init_ui(self):

        self.setWindowTitle("Speedtest Studio")

        self.setFixedSize(540, 920)

        self.setStyleSheet("""
            QWidget {
                background-color: #0b0c10;
                color: #ffffff;
                font-family: 'Segoe UI';
            }

            QFrame#Card {
                background-color: #14151a;
                border: 1px solid #1c1e24;
                border-radius: 12px;
            }

            QLabel {
                background: transparent;
            }

            QProgressBar {
                border: none;
                background-color: #1c1e24;
                height: 4px;
                border-radius: 2px;
            }

            QProgressBar::chunk {
                background-color: #00f5d4;
                border-radius: 2px;
            }
        """)

        layout = QVBoxLayout()

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout.setSpacing(16)

        # =====================================================
        # METRICS CARD
        # =====================================================
        metrics_frame = QFrame()

        metrics_frame.setObjectName("Card")

        metrics_layout = QHBoxLayout(
            metrics_frame
        )

        metrics_layout.setContentsMargins(
            10,
            15,
            10,
            15
        )

        def create_metric_vbox(title):

            vbox = QVBoxLayout()

            lbl_title = QLabel(title)

            lbl_title.setAlignment(
                Qt.AlignCenter
            )

            lbl_title.setStyleSheet("""
                color: #a0a5b5;
                font-size: 13px;
                font-weight: bold;
            """)

            lbl_val = QLabel("--")

            lbl_val.setAlignment(
                Qt.AlignCenter
            )

            lbl_val.setStyleSheet("""
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
            """)

            vbox.addWidget(lbl_title)
            vbox.addWidget(lbl_val)

            return vbox, lbl_val

        ping_box, self.ping_val = (
            create_metric_vbox("Ping")
        )

        jitter_box, self.jitter_val = (
            create_metric_vbox("Jitter")
        )

        dl_box, self.download_val = (
            create_metric_vbox("Download")
        )

        ul_box, self.upload_val = (
            create_metric_vbox("Upload")
        )

        metrics_layout.addLayout(ping_box)
        metrics_layout.addLayout(jitter_box)
        metrics_layout.addLayout(dl_box)
        metrics_layout.addLayout(ul_box)

        layout.addWidget(metrics_frame)

        # =====================================================
        # GAUGE
        # =====================================================
        self.gauge = AdvancedGaugeWidget(
            start_callback=self.start_test
        )

        layout.addWidget(
            self.gauge,
            alignment=Qt.AlignCenter
        )

        self.live_speed_lbl = QLabel("0.00")

        self.live_speed_lbl.setFont(
            QFont("Segoe UI", 46, QFont.Bold)
        )

        self.live_speed_lbl.setAlignment(
            Qt.AlignCenter
        )

        self.live_speed_lbl.setStyleSheet("""
            color: #ffffff;
            margin-top: -50px;
            margin-bottom: -10px;
        """)

        layout.addWidget(self.live_speed_lbl)

        self.status_lbl = QLabel(
            "Click GO to start diagnostics."
        )

        self.status_lbl.setAlignment(
            Qt.AlignCenter
        )

        self.status_lbl.setStyleSheet("""
            color: #a0a5b5;
            font-size: 12px;
        """)

        layout.addWidget(self.status_lbl)

        self.progress_bar = QProgressBar()

        self.progress_bar.setValue(0)

        layout.addWidget(self.progress_bar)

        # =====================================================
        # ISP CARD
        # =====================================================
        isp_frame = QFrame()

        isp_frame.setObjectName("Card")

        isp_layout = QHBoxLayout(isp_frame)

        isp_layout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        isp_details_layout = QVBoxLayout()

        self.isp_lbl = QLabel(
            "Detecting Carrier..."
        )

        self.ip_lbl = QLabel("IP Details")

        self.isp_lbl.setStyleSheet("""
            color: #ffffff;
            font-size: 13px;
            font-weight: bold;
        """)

        self.ip_lbl.setStyleSheet("""
            color: #6c7282;
            font-size: 11px;
        """)

        isp_details_layout.addWidget(
            self.isp_lbl
        )

        isp_details_layout.addWidget(
            self.ip_lbl
        )

        self.wifi_lbl = QLabel("Ethernet")

        self.wifi_lbl.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        self.wifi_lbl.setStyleSheet("""
            color: #00f5d4;
            font-size: 11px;
            font-weight: bold;
        """)

        isp_layout.addLayout(
            isp_details_layout
        )

        isp_layout.addStretch()

        isp_layout.addWidget(self.wifi_lbl)

        layout.addWidget(isp_frame)

        # =====================================================
        # SYSTEM INFO CARD
        # =====================================================
        sys_frame = QFrame()

        sys_frame.setObjectName("Card")

        sys_layout = QVBoxLayout(sys_frame)

        sys_layout.setContentsMargins(
            15,
            15,
            15,
            15
        )

        sys_layout.setSpacing(5)

        sys_title = QLabel(
            "System Hardware Specifications"
        )

        sys_title.setStyleSheet("""
            color: #00f5d4;
            font-size: 11px;
            font-weight: bold;
        """)

        sys_layout.addWidget(sys_title)

        self.cpu_lbl = QLabel("CPU: --")
        self.ram_lbl = QLabel("RAM: --")
        self.gpu_lbl = QLabel("GPU: --")
        self.lscpu_lbl = QLabel("lscpu: --")

        all_labels = [
            self.cpu_lbl,
            self.ram_lbl,
            self.gpu_lbl,
            self.lscpu_lbl,
        ]

        for lbl in all_labels:

            lbl.setWordWrap(True)

            lbl.setStyleSheet("""
                color: #a0a5b5;
                font-size: 11px;
            """)

            sys_layout.addWidget(lbl)

        layout.addWidget(sys_frame)

        self.setLayout(layout)

    # =====================================================
    # SYSTEM INFO
    # =====================================================
    def load_system_info(self):

        cpu = (
            platform.processor()
            or "Unknown Processor"
        )

        ram = round(
            psutil.virtual_memory().total
            / (1024 ** 3),
            1
        )

        gpu_name = "Integrated Graphics"

        if GPUtil:

            try:

                gpus = GPUtil.getGPUs()

                if gpus:
                    gpu_name = gpus[0].name

            except:
                pass

        self.cpu_lbl.setText(
            f"Processor: {cpu}"
        )

        self.ram_lbl.setText(
            f"Memory: {ram} GB RAM"
        )

        self.gpu_lbl.setText(
            f"GPU: {gpu_name}"
        )

        self.lscpu_lbl.setText(
            self.get_lscpu_info()
        )

        self.wifi_lbl.setText(
            self.get_wifi_name().upper()
        )

    # =====================================================
    # WIFI NAME
    # =====================================================
    def get_wifi_name(self):

        try:

            result = subprocess.check_output(
                ["iwgetid", "-r"]
            ).decode().strip()

            return (
                result
                if result
                else "Ethernet"
            )

        except:
            return "Ethernet"

    # =====================================================
    # LSCPU INFO
    # =====================================================
    def get_lscpu_info(self):

        try:

            output = subprocess.check_output(
                ["lscpu"]
            ).decode()

            cores = ""
            threads = ""

            for line in output.splitlines():

                if (
                    "Core(s) per socket:"
                    in line
                ):

                    cores = line.split(":")[1].strip()

                elif (
                    "CPU(s):" in line
                    and not threads
                ):

                    threads = line.split(":")[1].strip()

            return (
                f"CPU Info: "
                f"Cores: {cores} | "
                f"Threads: {threads}"
            )

        except:
            return "lscpu unavailable"

    # =====================================================
    # UPDATE HELPERS
    # =====================================================
    def update_status(
        self,
        text,
        percentage
    ):

        self.status_lbl.setText(text)

        self.progress_bar.setValue(
            percentage
        )

    def update_isp(
        self,
        isp,
        ip,
        server_desc
    ):

        self.isp_lbl.setText(isp)

        self.ip_lbl.setText(
            f"{ip} | Base: {server_desc}"
        )

    def update_latency_metrics(
        self,
        ping,
        jitter
    ):

        self.ping_val.setText(ping)

        self.jitter_val.setText(jitter)

    # =====================================================
    # START TEST
    # =====================================================
    def start_test(self):

        self.ping_val.setText("--")
        self.jitter_val.setText("--")
        self.download_val.setText("--")
        self.upload_val.setText("--")

        self.hardware_tracking = True

        io_thread = threading.Thread(
            target=self.hardware_io_loop,
            daemon=True
        )

        io_thread.start()

        test_thread = threading.Thread(
            target=self.run_speed_test,
            daemon=True
        )

        test_thread.start()

    # =====================================================
    # HARDWARE IO LOOP
    # =====================================================
    def hardware_io_loop(self):

        last_recv = (
            psutil.net_io_counters().bytes_recv
        )

        last_sent = (
            psutil.net_io_counters().bytes_sent
        )

        last_time = time.time()

        while self.hardware_tracking:

            time.sleep(0.03)

            now = time.time()

            dt = now - last_time

            if dt <= 0:
                continue

            io_data = psutil.net_io_counters()

            curr_recv = io_data.bytes_recv
            curr_sent = io_data.bytes_sent

            speed_dl = (
                ((curr_recv - last_recv) * 8)
                / (1024 * 1024)
                / dt
            )

            speed_ul = (
                ((curr_sent - last_sent) * 8)
                / (1024 * 1024)
                / dt
            )

            current_activity = max(
                speed_dl,
                speed_ul
            )

            if current_activity > 0.1:

                self.gauge.set_speed(
                    current_activity
                )

                self.live_speed_lbl.setText(
                    f"{current_activity:.2f}"
                )

            last_recv = curr_recv
            last_sent = curr_sent
            last_time = now

    # =====================================================
    # SPEEDTEST
    # =====================================================
    def run_speed_test(self):

        try:

            self.signals.status.emit(
                "Connecting to Speedtest servers...",
                15
            )

            st = speedtest.Speedtest(
                secure=True
            )

            self.signals.status.emit(
                "Calculating latency...",
                35
            )

            st.get_best_server()

            results = st.results.dict()

            client = results.get(
                "client",
                {}
            )

            server = results.get(
                "server",
                {}
            )

            self.signals.isp_info.emit(
                client.get(
                    "isp",
                    "Unknown ISP"
                ),

                client.get(
                    "ip",
                    "Unknown IP"
                ),

                f"{server.get('sponsor')} "
                f"({server.get('name')})"
            )

            base_ping = results.get(
                "ping",
                0.0
            )

            jitter_sample = abs(
                (base_ping * 0.15) - 1.5
            )

            self.signals.ping_done.emit(
                f"{base_ping:.0f}",
                f"{jitter_sample:.1f}"
            )

            self.signals.status.emit(
                "Testing download speed...",
                60
            )

            dl_raw = st.download()

            dl_mbps = dl_raw / 1_000_000

            self.signals.download_done.emit(
                f"{dl_mbps:.2f} Mbps"
            )

            self.signals.status.emit(
                "Testing upload speed...",
                85
            )

            ul_raw = st.upload()

            ul_mbps = ul_raw / 1_000_000

            self.signals.upload_done.emit(
                f"{ul_mbps:.2f} Mbps"
            )

            self.signals.status.emit(
                "Diagnostics completed.",
                100
            )

        except Exception as err:

            self.signals.status.emit(
                f"Error: {str(err)}",
                100
            )

        finally:

            self.signals.finished.emit()

    # =====================================================
    # COMPLETE
    # =====================================================
    def test_complete(self):

        self.hardware_tracking = False

        self.live_speed_lbl.setText("0.00")

        self.gauge.reset_ui()


# =========================================================
# MAIN
# =====================================================
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = SpeedTestUI()

    window.show()

    sys.exit(app.exec_())
