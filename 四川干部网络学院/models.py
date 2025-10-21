# models.py
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified

# 创建 db 实例，但不绑定 app（在 app.py 中绑定）
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    # 可以添加更多字段，如 created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """将模型实例转换为字典，便于 JSON 序列化"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }


class ScgbTask(db.Model):
    __tablename__ = 'scgb_task'  # 指定表名
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'comment': '四川干部任务记录'
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    nick_name = db.Column(db.String(100), nullable=False, comment="账号")
    organ_name = db.Column(db.String(256), nullable=False, comment="账号")
    username = db.Column(db.String(100), nullable=False, comment="账号")
    password = db.Column(db.String(100), nullable=False, comment="密码")
    is_head = db.Column(db.String(100), nullable=False, comment="是否浏览器无头模式（1：有头，0：无头）")
    status = db.Column(db.String(8), comment="状态（1：未完成，2：完成）")
    is_running = db.Column(db.String(8), comment="是否运行（0：未运行，1：运行中）")
    class_id = db.Column(db.String(256), comment="课程id")
    no_play_videos = db.Column(db.JSON, comment="不播放列表")  # MySQL JSON 类型
    required_period = db.Column(db.String(256), comment="必修时间")
    elective_period = db.Column(db.String(256), comment="选修时间")
    courses = db.Column(db.JSON, comment="不播放列表")  # MySQL JSON 类型
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建日期')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新日期')

    def to_dict(self):
        """将模型实例转换为字典，便于 JSON 序列化"""
        return {
            'id': self.id,
            'nick_name': self.nick_name,
            'organ_name': self.organ_name,
            'username': self.username,
            'password': '******',  # 安全起见，返回时不暴露密码
            'is_head': self.is_head,
            'status': self.status,
            'is_running': self.is_running,
            'class_id': self.class_id,
            'no_play_videos': self.no_play_videos,
            'required_period': self.required_period,
            'elective_period': self.elective_period,
            'courses': self.courses,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None
        }

    def __repr__(self):
        return f'<ScgbTask {self.username} - {self.status}>'

    @classmethod
    def update_by_id(cls, task_id, **kwargs):
        """
        根据 ID 更新 ScgbTask 记录（支持 JSON 字段）
        """
        try:
            task = cls.query.get(task_id)
            if not task:
                return False, "任务不存在"

            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)

                    # ✅ 如果是 JSON 类型字段，标记为已修改
                    if isinstance(getattr(cls, key).type, db.JSON):
                        flag_modified(task, key)
                else:
                    raise AttributeError(f"ScgbTask 没有属性 '{key}'")

            task.update_time = datetime.now()
            db.session.commit()
            return True, "更新成功"
        except Exception as e:
            db.session.rollback()
            print(f"更新失败: {str(e)}")
            return False, f"更新失败: {str(e)}"


class ScgbCourse(db.Model):
    __tablename__ = 'scgb_course'  # 数据库表名

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    class_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    courses = db.Column(db.JSON, comment="不播放列表")  # MySQL JSON 类型
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建日期')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新日期')

    # 可以添加更多字段，如 created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<User {self.name}>'

    def to_dict(self):
        """将模型实例转换为字典，便于 JSON 序列化"""
        return {
            'id': self.id,
            'class_id': self.class_id,
            'name': self.name,
            'courses': self.courses,
        }
