from datetime import datetime

from . import db


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nick_name = db.Column(db.String(100), default='', comment='姓名')
    organ_name = db.Column(db.String(256), comment='单位名称')
    username = db.Column(db.String(100), nullable=False, comment='账号')
    password = db.Column(db.String(100), nullable=False, comment='密码')
    is_head = db.Column(db.String(100), nullable=False, default='1', comment='是否浏览器无头模式（1：无头，0：有头）')
    is_charged = db.Column(db.String(8), nullable=False, default='0', comment='是否收费（1：收费，0：不收费）')
    price = db.Column(db.Integer, nullable=True, default=None, comment='价格')
    status = db.Column(db.String(8), default='1', comment='状态（1：未完成，2：完成）')
    progress = db.Column(db.String(64), default='', comment='学习进度（按网站不同：学时或完成数/总数）')
    no_play_videos = db.Column(db.JSON, comment='不播放列表')
    remark = db.Column(db.String(100), comment='备注')
    class_id = db.Column(db.String(256), comment='课程id')
    courses = db.Column(db.JSON, comment='特定课表')
    website_code = db.Column(db.String(256), comment='网站编码')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建日期')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新日期')
    completed_time = db.Column(db.DateTime, nullable=True, default=None, comment='完成时间')

    def to_dict(self, include_courses=True):
        data = {
            'id': self.id,
            'nick_name': self.nick_name,
            'organ_name': self.organ_name,
            'username': self.username,
            'password': self.password,
            'is_head': self.is_head,
            'is_charged': self.is_charged,
            'price': int(self.price) if self.price is not None else None,
            'status': self.status,
            'progress': self.progress or '',
            'no_play_videos': self.no_play_videos,
            'remark': self.remark,
            'class_id': self.class_id,
            'website_code': self.website_code,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'completed_time': (
                self.completed_time.strftime('%Y-%m-%d %H:%M:%S') if self.completed_time else None
            ),
        }
        # 列表场景可跳过 courses，避免触发 deferred 懒加载
        if include_courses:
            data['courses'] = self.courses
        else:
            data['courses'] = None
        return data
