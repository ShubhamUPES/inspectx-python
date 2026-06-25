import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter, QLinearGradient

from app.ui.theme import (
    DARK_BG, VIOLET_600, VIOLET_500, VIOLET_400, VIOLET_700,
    GRAY_400, GRAY_500, GRAY_700, WHITE, RED_400,
)
from app.services.auth_service import login

LOGO_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "hestabit-logo.jpg")
)

HIGHLIGHTS = [
    "Precision defect annotation tools",
    "Sub-30ms real-time inference",
    "Industrial PLC & protocol support",
    "Live inspection & active learning",
]


class LoginPage(QWidget):
    login_success = pyqtSignal(object)   # emits User object

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        self.setStyleSheet(f"background: {DARK_BG};")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_left(), 5)
        root.addWidget(self._build_right(), 7)

    # ── Left branding panel ────────────────────────────────────────────────────
    def _build_left(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet("background: #0F0A2E;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(48, 48, 48, 36)
        layout.setSpacing(0)

        # Logo + name
        logo_row = QWidget()
        logo_row.setStyleSheet("background:transparent;")
        lr = QHBoxLayout(logo_row)
        lr.setContentsMargins(0, 0, 0, 0)
        lr.setSpacing(12)
        logo = QLabel()
        if os.path.exists(LOGO_PATH):
            px = QPixmap(LOGO_PATH).scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(px)
        logo.setStyleSheet("background:transparent;border:none;")
        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        b1 = QLabel("Hestabit Defect Detection Studio")
        b1.setStyleSheet(f"font-size:14px;font-weight:700;color:{WHITE};background:transparent;border:none;")
        b2 = QLabel("Industrial AI Vision Platform")
        b2.setStyleSheet(f"font-size:11px;color:{VIOLET_400};background:transparent;border:none;")
        brand_col.addWidget(b1)
        brand_col.addWidget(b2)
        lr.addWidget(logo)
        lr.addLayout(brand_col)
        lr.addStretch()
        layout.addWidget(logo_row)
        layout.addStretch()

        # Hero text
        tag = QLabel("Industrial AI Vision Platform")
        tag.setStyleSheet(f"""
            font-size:11px;font-weight:600;color:{VIOLET_400};
            background:rgba(139,92,246,0.12);
            border:1px solid rgba(139,92,246,0.3);
            border-radius:20px;padding:4px 12px;
        """)
        tag.setFixedWidth(200)
        layout.addWidget(tag)
        layout.addSpacing(16)

        hero = QLabel("From raw data to\nproduction inspection\nin minutes.")
        hero.setStyleSheet(f"font-size:28px;font-weight:800;color:{WHITE};background:transparent;border:none;line-height:1.3;")
        hero.setWordWrap(True)
        layout.addWidget(hero)
        layout.addSpacing(12)

        sub = QLabel("The complete platform for training, deploying, and running\nAI-powered defect detection on the factory floor.")
        sub.setStyleSheet(f"font-size:12px;color:{GRAY_400};background:transparent;border:none;")
        sub.setWordWrap(True)
        layout.addWidget(sub)
        layout.addSpacing(28)

        for txt in HIGHLIGHTS:
            row = QWidget()
            row.setStyleSheet("background:transparent;border:none;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(10)
            dot = QLabel("✦")
            dot.setStyleSheet(f"color:{VIOLET_400};background:transparent;border:none;font-size:11px;")
            dot.setFixedWidth(14)
            lbl = QLabel(txt)
            lbl.setStyleSheet(f"color:#D1D5DB;font-size:12px;background:transparent;border:none;")
            rl.addWidget(dot)
            rl.addWidget(lbl)
            rl.addStretch()
            layout.addWidget(row)
            layout.addSpacing(6)

        layout.addStretch()
        copy = QLabel("© 2026 Hestabit Technologies")
        copy.setStyleSheet(f"font-size:10px;color:#374151;background:transparent;border:none;")
        layout.addWidget(copy)
        return panel

    # ── Right login form ───────────────────────────────────────────────────────
    def _build_right(self) -> QWidget:
        panel = QWidget()
        panel.setStyleSheet(f"background:{DARK_BG};")
        outer = QVBoxLayout(panel)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.setContentsMargins(60, 60, 60, 60)

        form = QWidget()
        form.setMaximumWidth(360)
        form.setStyleSheet(f"background:transparent;")
        fl = QVBoxLayout(form)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(0)

        title = QLabel("Welcome back")
        title.setStyleSheet(f"font-size:26px;font-weight:800;color:{WHITE};background:transparent;border:none;")
        sub = QLabel("Sign in to your workspace to continue.")
        sub.setStyleSheet(f"font-size:12px;color:{GRAY_500};background:transparent;border:none;")
        fl.addWidget(title)
        fl.addSpacing(4)
        fl.addWidget(sub)
        fl.addSpacing(28)

        # Email / username field
        email_lbl = QLabel("EMAIL OR USERNAME")
        email_lbl.setStyleSheet(f"font-size:10px;font-weight:600;letter-spacing:0.08em;color:{GRAY_400};background:transparent;border:none;")
        fl.addWidget(email_lbl)
        fl.addSpacing(6)
        self._email = QLineEdit()
        self._email.setPlaceholderText("you@company.com or username")
        self._email.setStyleSheet(self._input_css())
        self._email.setFixedHeight(46)
        fl.addWidget(self._email)
        self._email_err = QLabel("")
        self._email_err.setStyleSheet(f"font-size:11px;color:{RED_400};background:transparent;border:none;")
        self._email_err.hide()
        fl.addWidget(self._email_err)
        fl.addSpacing(16)

        # Password field
        pwd_lbl = QLabel("PASSWORD")
        pwd_lbl.setStyleSheet(f"font-size:10px;font-weight:600;letter-spacing:0.08em;color:{GRAY_400};background:transparent;border:none;")
        fl.addWidget(pwd_lbl)
        fl.addSpacing(6)
        pwd_row = QWidget()
        pwd_row.setStyleSheet("background:transparent;border:none;")
        pr = QHBoxLayout(pwd_row)
        pr.setContentsMargins(0, 0, 0, 0)
        pr.setSpacing(0)
        self._pwd = QLineEdit()
        self._pwd.setPlaceholderText("••••••••")
        self._pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self._pwd.setStyleSheet(self._input_css())
        self._pwd.setFixedHeight(46)
        self._show_btn = QPushButton("Show")
        self._show_btn.setFixedSize(54, 46)
        self._show_btn.setStyleSheet(f"""
            QPushButton {{
                background:transparent;color:{GRAY_500};
                border:none;font-size:11px;font-weight:600;
            }}
            QPushButton:hover {{ color:{WHITE}; }}
        """)
        self._show_btn.clicked.connect(self._toggle_password)
        pr.addWidget(self._pwd, 1)
        pr.addWidget(self._show_btn)
        fl.addWidget(pwd_row)
        self._pwd_err = QLabel("")
        self._pwd_err.setStyleSheet(f"font-size:11px;color:{RED_400};background:transparent;border:none;")
        self._pwd_err.hide()
        fl.addWidget(self._pwd_err)
        fl.addSpacing(24)

        # Submit
        self._submit_btn = QPushButton("Sign In")
        self._submit_btn.setFixedHeight(48)
        self._submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._submit_btn.setStyleSheet(f"""
            QPushButton {{
                background:{VIOLET_600};color:{WHITE};
                border:none;border-radius:12px;
                font-size:14px;font-weight:700;
            }}
            QPushButton:hover {{ background:{VIOLET_500}; }}
            QPushButton:disabled {{ background:#3D3862;color:{GRAY_500}; }}
        """)
        self._submit_btn.clicked.connect(self._handle_submit)
        self._email.returnPressed.connect(self._handle_submit)
        self._pwd.returnPressed.connect(self._handle_submit)
        fl.addWidget(self._submit_btn)
        fl.addSpacing(16)

        hint = QLabel("Admin: admin / admin   ·   Demo: demo@inspectx.ai / demo1234")
        hint.setStyleSheet(f"font-size:11px;color:{GRAY_500};background:transparent;border:none;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(hint)

        # Error
        self._general_err = QLabel("")
        self._general_err.setStyleSheet(
            f"font-size:12px;color:{RED_400};background:rgba(220,38,38,0.1);"
            f"border:1px solid rgba(220,38,38,0.2);border-radius:8px;padding:8px;"
        )
        self._general_err.setWordWrap(True)
        self._general_err.hide()
        fl.addWidget(self._general_err)

        outer.addStretch()
        outer.addWidget(form, 0, Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch()
        return panel

    def _input_css(self) -> str:
        return f"""
            QLineEdit {{
                background:rgba(255,255,255,0.05);
                color:{WHITE};
                border:1px solid rgba(255,255,255,0.1);
                border-radius:12px;
                padding:0 14px;
                font-size:13px;
            }}
            QLineEdit:focus {{
                border-color:{VIOLET_500};
                background:rgba(255,255,255,0.08);
            }}
            QLineEdit::placeholder {{ color:#4B5563; }}
        """

    def _toggle_password(self):
        if self._pwd.echoMode() == QLineEdit.EchoMode.Password:
            self._pwd.setEchoMode(QLineEdit.EchoMode.Normal)
            self._show_btn.setText("Hide")
        else:
            self._pwd.setEchoMode(QLineEdit.EchoMode.Password)
            self._show_btn.setText("Show")

    def _handle_submit(self):
        email = self._email.text().strip()
        password = self._pwd.text()
        valid = True

        self._email_err.hide()
        self._pwd_err.hide()
        self._general_err.hide()

        if not email:
            self._email_err.setText("Email or username is required")
            self._email_err.show()
            valid = False

        if not password:
            self._pwd_err.setText("Password is required")
            self._pwd_err.show()
            valid = False
        elif len(password) < 4:
            self._pwd_err.setText("Password must be at least 4 characters")
            self._pwd_err.show()
            valid = False

        if not valid:
            return

        self._submit_btn.setEnabled(False)
        self._submit_btn.setText("Signing in…")

        # Attempt login (or auto-register for demo)
        QTimer.singleShot(400, lambda: self._do_login(email, password))

    def _do_login(self, email: str, password: str):
        from app.services.auth_service import register
        user = login(email, password)
        if not user:
            # Auto-register for demo
            try:
                user = register(email, password)
            except ValueError:
                self._general_err.setText("Incorrect password for this account.")
                self._general_err.show()
                self._submit_btn.setEnabled(True)
                self._submit_btn.setText("Sign In")
                return

        self._submit_btn.setEnabled(True)
        self._submit_btn.setText("Sign In")
        self.login_success.emit(user)
