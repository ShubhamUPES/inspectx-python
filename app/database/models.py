import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    type = Column(String, default="detection")
    status = Column(String, default="Active")
    source = Column(String, default="No Data")
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    labels_json = Column(Text, default="[]")
    tags_json = Column(Text, default='["train","review","failed-sample","production"]')
    camera_json = Column(Text, default="{}")
    communication_json = Column(Text, default="{}")
    runtime_json = Column(Text, default='{"online":false,"running":false,"paused":false,"result":"IDLE","total":0,"pass":0,"fail":0,"alarm":"Offline","last":"Never","inference":"Idle"}')
    signals_json = Column(Text, default='{"Trigger":false,"Reset":false,"PASS":false,"FAIL":false,"Reject":false,"Heartbeat":false,"Busy":false,"Alarm":false}')
    active_model_id = Column(Integer, nullable=True)
    active_version_id = Column(Integer, nullable=True)
    selected_image_id = Column(Integer, nullable=True)

    user = relationship("User", back_populates="projects")
    images = relationship("Image", back_populates="project", cascade="all, delete-orphan",
                          order_by="Image.created_at")
    versions = relationship("Version", back_populates="project", cascade="all, delete-orphan",
                            order_by="Version.created_at.desc()")
    ml_models = relationship("MLModel", back_populates="project", cascade="all, delete-orphan",
                             order_by="MLModel.trained_at.desc()")
    logs = relationship("Log", back_populates="project", cascade="all, delete-orphan",
                        order_by="Log.created_at.desc()")

    @property
    def labels(self):
        return json.loads(self.labels_json or "[]")

    @labels.setter
    def labels(self, value):
        self.labels_json = json.dumps(value)

    @property
    def tags(self):
        return json.loads(self.tags_json or "[]")

    @tags.setter
    def tags(self, value):
        self.tags_json = json.dumps(value)

    @property
    def camera(self):
        default = {
            "selected": "", "profile": "No saved profile", "connected": False, "live": False,
            "profiles": [], "resolution": "1920 x 1080", "exposure": 5200, "gain": 12,
            "fps": 30, "trigger": "Manual Trigger", "roiSaved": False,
        }
        saved = json.loads(self.camera_json or "{}")
        return {**default, **saved}

    @camera.setter
    def camera(self, value):
        self.camera_json = json.dumps(value)

    @property
    def communication(self):
        default = {
            "protocol": "EtherNet/IP", "status": "Not Saved",
            "ip": "192.168.1.10", "port": "44818",
            "deviceName": "Defect_Detection_Cell_01",
            "trigger": "Trigger_In", "result": "Result_Out",
            "heartbeat": "Heartbeat", "pass": "PASS_Out",
            "fail": "FAIL_Out", "reject": "Reject_Out", "alarm": "Alarm_Out",
        }
        saved = json.loads(self.communication_json or "{}")
        return {**default, **saved}

    @communication.setter
    def communication(self, value):
        self.communication_json = json.dumps(value)

    @property
    def runtime(self):
        return json.loads(self.runtime_json or "{}")

    @runtime.setter
    def runtime(self, value):
        self.runtime_json = json.dumps(value)

    @property
    def signals(self):
        return json.loads(self.signals_json or "{}")

    @signals.setter
    def signals(self, value):
        self.signals_json = json.dumps(value)

    @property
    def failed_samples(self):
        return [img for img in self.images if img.failed]

    def annotated_count(self):
        return sum(1 for img in self.images if img.status == "Annotated")

    def updated_str(self):
        delta = datetime.utcnow() - self.updated_at
        if delta.seconds < 60:
            return "Just now"
        if delta.seconds < 3600:
            return f"{delta.seconds // 60}m ago"
        if delta.days == 0:
            return f"{delta.seconds // 3600}h ago"
        return self.updated_at.strftime("%Y-%m-%d")


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, nullable=False)
    file_path = Column(String, default="")
    source = Column(String, default="Upload")
    status = Column(String, default="Unannotated")
    split = Column(String, default="Train")
    prediction = Column(String, default="None")
    failed = Column(Boolean, default=False)
    labels_json = Column(Text, default="[]")
    tags_json = Column(Text, default='["train"]')
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="images")
    annotations = relationship("Annotation", back_populates="image",
                               cascade="all, delete-orphan")
    version_links = relationship("VersionImage", back_populates="image",
                                 cascade="all, delete-orphan")

    @property
    def labels(self):
        return json.loads(self.labels_json or "[]")

    @labels.setter
    def labels(self, value):
        self.labels_json = json.dumps(value)

    @property
    def tags(self):
        return json.loads(self.tags_json or "[]")

    @tags.setter
    def tags(self, value):
        self.tags_json = json.dumps(value)


class Annotation(Base):
    __tablename__ = "annotations"
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    ann_type = Column(String, default="bbox")
    label = Column(String, default="")
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    w = Column(Float, default=0.0)
    h = Column(Float, default=0.0)
    points_json = Column(Text, default="[]")
    pending = Column(Boolean, default=False)

    image = relationship("Image", back_populates="annotations")

    @property
    def points(self):
        return json.loads(self.points_json or "[]")

    @points.setter
    def points(self, value):
        self.points_json = json.dumps(value)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.ann_type,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "points": self.points,
            "pending": self.pending,
        }


class Version(Base):
    __tablename__ = "versions"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    snapshot_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    image_count = Column(Integer, default=0)
    annotated_count = Column(Integer, default=0)
    generated_count = Column(Integer, default=0)
    notes = Column(Text, default="")
    preprocessing_json = Column(Text, default='["Auto Orient","Resize 640"]')
    augmentation_json = Column(Text, default='["Flip","Rotate","Brightness"]')
    transforms_json = Column(Text, default='["Normalize","Pad to square"]')
    split_ratio = Column(String, default="80 / 15 / 5")
    ready = Column(Boolean, default=True)

    project = relationship("Project", back_populates="versions")
    ml_models = relationship("MLModel", back_populates="version")
    version_images = relationship("VersionImage", back_populates="version",
                                  cascade="all, delete-orphan")

    @property
    def preprocessing(self):
        return json.loads(self.preprocessing_json or "[]")

    @preprocessing.setter
    def preprocessing(self, value):
        self.preprocessing_json = json.dumps(value)

    @property
    def augmentation(self):
        return json.loads(self.augmentation_json or "[]")

    @augmentation.setter
    def augmentation(self, value):
        self.augmentation_json = json.dumps(value)

    @property
    def transforms(self):
        return json.loads(self.transforms_json or "[]")

    @transforms.setter
    def transforms(self, value):
        self.transforms_json = json.dumps(value)

    @property
    def image_ids(self):
        return [vi.image_id for vi in self.version_images]

    def created_str(self):
        return self.created_at.strftime("%Y-%m-%d")


class VersionImage(Base):
    __tablename__ = "version_images"
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("versions.id"))
    image_id = Column(Integer, ForeignKey("images.id"))

    version = relationship("Version", back_populates="version_images")
    image = relationship("Image", back_populates="version_links")


class MLModel(Base):
    __tablename__ = "ml_models"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=True)
    name = Column(String)
    version_label = Column(String)
    dataset_version = Column(String, default="")
    map_score = Column(String, default="0%")
    precision = Column(String, default="0%")
    recall = Column(String, default="0%")
    latency = Column(String, default="0 ms")
    deployment = Column(String, default="Registry")
    trained_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="ml_models")
    version = relationship("Version", back_populates="ml_models")

    def updated_str(self):
        delta = datetime.utcnow() - self.updated_at
        if delta.seconds < 60:
            return "Just now"
        return self.updated_at.strftime("%Y-%m-%d %H:%M")


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    log_type = Column(String)
    time_str = Column(String)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="logs")
