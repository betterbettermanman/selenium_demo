from datetime import datetime

from . import db


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), default='', comment='课程名称')
    class_id = db.Column(db.String(100), comment='课程id')
    website_code = db.Column(db.String(256), comment='网站编码')
    courses = db.Column(db.JSON, comment='特定课表')
    remark = db.Column(db.String(100), comment='备注')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建日期')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新日期')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'class_id': self.class_id,
            'website_code': self.website_code,
            'courses': self.courses,
            'remark': self.remark,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
        }
