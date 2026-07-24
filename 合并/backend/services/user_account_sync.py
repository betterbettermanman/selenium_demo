from models import db
from models.user_account import UserAccount


def sync_user_account_from_task(*, website_code, username, password, nick_name='', organ_name=None):
    """根据网站编码和账号同步用户表：不存在则新增，已存在则同步密码/姓名/单位。"""
    if not website_code or not username or not password:
        return

    account = UserAccount.query.filter_by(
        website_code=website_code,
        username=username,
    ).first()

    nick_name = nick_name or ''

    if account is None:
        db.session.add(UserAccount(
            website_code=website_code,
            username=username,
            password=password,
            nick_name=nick_name,
            organ_name=organ_name,
        ))
        return

    if account.password != password:
        account.password = password
    if account.nick_name != nick_name:
        account.nick_name = nick_name
    if organ_name is not None and account.organ_name != organ_name:
        account.organ_name = organ_name
