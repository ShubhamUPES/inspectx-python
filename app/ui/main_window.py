"""
MainWindow — top-level application window.
Hosts either the LoginPage / HomePage or the project workspace (sidebar + pages).
"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QHBoxLayout,
    QVBoxLayout, QApplication,
)
from PyQt6.QtCore import Qt

from app.ui.state import AppState
from app.ui.pages.login_page   import LoginPage
from app.ui.pages.home_page    import HomePage
from app.ui.pages.overview_page  import OverviewPage
from app.ui.pages.annotate_page  import AnnotatePage, UploadPage
from app.ui.pages.dataset_page   import DatasetPage
from app.ui.pages.versions_page  import VersionsPage
from app.ui.pages.classes_page   import ClassesPage
from app.ui.pages.train_page     import TrainPage
from app.ui.pages.models_page    import ModelsPage
from app.ui.pages.test_page      import TestPage
from app.ui.pages.settings_page  import SettingsPage
from app.ui.widgets.sidebar      import ProjectSidebar
from app.ui.widgets.topbar       import TopBar
from app.ui.widgets.toast        import Toast


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InspectX —  Defect Detection Studio")
        self.resize(1400, 880)
        self.setMinimumSize(1100, 700)

        self._state = AppState(self)
        self._state.notification.connect(self._show_toast)

        self._root_stack = QStackedWidget()
        self.setCentralWidget(self._root_stack)

        # ── Auth screens ──────────────────────────────────────────────────────
        self._login_page = LoginPage()
        self._login_page.login_success.connect(self._on_login)
        self._root_stack.addWidget(self._login_page)      # index 0

        self._home_page = HomePage()
        self._home_page.open_project.connect(self._open_project)
        self._home_page.create_project.connect(self._create_project)
        self._root_stack.addWidget(self._home_page)       # index 1

        # ── Project workspace ─────────────────────────────────────────────────
        self._workspace = self._build_workspace()
        self._root_stack.addWidget(self._workspace)       # index 2

        self._root_stack.setCurrentIndex(0)

    # ── Workspace builder ──────────────────────────────────────────────────────

    def _build_workspace(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:#0F0E2A;")
        hl = QHBoxLayout(w)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)

        self._sidebar = ProjectSidebar()
        self._sidebar.route_changed.connect(self._navigate)
        self._sidebar.back_home.connect(self._go_home)
        hl.addWidget(self._sidebar)

        # Right: topbar + page stack
        right = QWidget()
        right.setStyleSheet("background:#F1F5F9;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._topbar = TopBar()
        rl.addWidget(self._topbar)

        self._page_stack = QStackedWidget()
        rl.addWidget(self._page_stack, 1)

        hl.addWidget(right, 1)

        # ── Pages ─────────────────────────────────────────────────────────────
        self._pages: dict[str, QWidget] = {}
        self._toast = Toast(right)

        def _add(route: str, page: QWidget):
            self._pages[route] = page
            self._page_stack.addWidget(page)

        overview = OverviewPage(self._state)
        overview.navigate.connect(self._navigate)
        _add("overview", overview)

        upload = UploadPage(self._state)
        upload.navigate.connect(self._navigate)
        _add("upload", upload)

        annotate = AnnotatePage(self._state)
        annotate.navigate.connect(self._navigate)
        _add("annotate", annotate)

        dataset = DatasetPage(self._state)
        dataset.navigate.connect(self._navigate)
        _add("dataset", dataset)

        versions = VersionsPage(self._state)
        versions.navigate.connect(self._navigate)
        _add("versions", versions)

        classes = ClassesPage(self._state)
        _add("classes", classes)

        train = TrainPage(self._state)
        _add("train", train)

        models = ModelsPage(self._state)
        models.navigate.connect(self._navigate)
        _add("models", models)

        test = TestPage(self._state)
        _add("test", test)

        settings = SettingsPage(self._state)
        settings.logout_requested.connect(self._logout)
        _add("settings", settings)

        return w

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _navigate(self, route: str):
        page = self._pages.get(route)
        if page:
            self._page_stack.setCurrentWidget(page)
        project_name = self._state.project.name if self._state.project else ""
        self._topbar.set_route(route, project_name)
        self._sidebar.set_route(route)

    # ── Auth flow ───────────────────────────────────────────────────────────────

    def _on_login(self, user):
        self._state.set_user(user)
        projects = self._state.load_projects()
        self._home_page.set_user(user)
        self._home_page.load_projects(projects)
        self._root_stack.setCurrentIndex(1)

    def _go_home(self):
        projects = self._state.load_projects()
        self._home_page.load_projects(projects)
        self._root_stack.setCurrentIndex(1)

    def _logout(self):
        self._state.logout()
        self._root_stack.setCurrentIndex(0)

    # ── Project flow ────────────────────────────────────────────────────────────

    def _open_project(self, project_id: int):
        self._state.open_project(project_id)
        project = self._state.project
        type_label = "Object Detection" if project.type == "detection" else "Instance Segmentation"
        self._sidebar.set_project(project.name, type_label)
        self._navigate("overview")
        self._root_stack.setCurrentIndex(2)

    def _create_project(self, name: str, project_type: str):
        self._state.create_project(name, project_type)
        project = self._state.project
        type_label = "Object Detection" if project.type == "detection" else "Instance Segmentation"
        self._sidebar.set_project(project.name, type_label)
        self._navigate("upload")
        self._root_stack.setCurrentIndex(2)

    # ── Toast ───────────────────────────────────────────────────────────────────

    def _show_toast(self, message: str):
        # Show on home_page or workspace depending on which is active
        if self._root_stack.currentIndex() == 1:
            self._home_page.notify(message)
        else:
            self._toast.show_message(message)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._toast._reposition()
