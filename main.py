import datetime
from generator import DjangonautsReport
from core.utils import create_argument_parser
from core.config import update_logger_level

if __name__ == "__main__":
    parser = create_argument_parser()
    args = parser.parse_args()
    if args.verbose:
        update_logger_level()

    today = datetime.date.today()
    last_week_monday = today - datetime.timedelta(days=today.weekday() + 7)
    last_week_sunday = last_week_monday + datetime.timedelta(days=6)

    end_date = args.end_date
    if not end_date:
        end_date = last_week_sunday

    start_date = args.start_date
    if not start_date:
        start_date = last_week_monday

    report = DjangonautsReport(
        start_date=start_date,
        end_date=end_date,
    )
    report.run()
