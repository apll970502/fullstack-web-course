"""DB 연결은 phase02/common/db.py 한 곳에서 관리한다. (.env 도 phase02/.env)"""
import sys
from pathlib import Path

# chapter10 에서 실행해도 phase02/common 을 import 할 수 있게 경로 추가
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from common.db import get_connection  # noqa: E402,F401
