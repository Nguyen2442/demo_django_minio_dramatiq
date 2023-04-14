import dramatiq
import asyncio, os, logging
from .broker import broker_rqm
from file_handler.models import FileTemplate
from core.tools import create_basic_file_excel
from core.database.minio import minio_client
from datetime import datetime

logger = logging.getLogger('Handler File')

@dramatiq.actor(
    broker=broker_rqm,
    queue_name="file_handler", 
    time_limit = 3600000,
    max_retries = 4
)
def process_file(message, *args, **kwargs):
    try: 
        start_at = datetime.timestamp(datetime.utcnow())
        logger.info(f'Start process prepare file excel {message.get("name")}.xlsx at {start_at}')
        asyncio.run(generate_file_excel_in_database(message))
        logger.info(f'Done process prepare file excel {message.get("name")}.xlsx at {datetime.timestamp(datetime.utcnow())} excute about {datetime.timestamp(datetime.utcnow())-start_at}s')
    except Exception as e:
        raise dramatiq.Retry(message=e, delay=600000)


def generate_file_excel_in_database(message):
    header = [
        "STT", "header1", "header2",
        "header3", "header4", "header5",
        "header6", "header7", "header8",
        "header9", "header10", "header11",
        "header12", "header13"
    ]
    count = 1
    workbook, worksheet = create_basic_file_excel(header)
    
    file_data = FileTemplate.objects.all().order_by("-id")[:50000]
    for data in file_data:
        row = [
            count, data.get("header_1"), data.get("header_2"), data.get("header_3"),
            data.get("header_4"), data.get("header_5"), data.get("header_6"),
            data.get("header_7"), data.get("header_8"), data.get("header_9"),
            data.get("header_10"), data.get("header_11"), data.get("header_12"), data.get("header_13")
        ]
        worksheet.append(row)
        count +=1
    name_file =  message.get('name')
    folder = message.get('type')
    file_path = f'statics/{folder}/{name_file}.xlsx'
    workbook.save(file_path)
    check_path = os.path.isfile(file_path)
    if check_path:
        file_size = os.path.getsize(file_path)
        with open(file_path, "rb") as file:
            try:
                minio_client.client.put_object(
                    folder,
                    f'{name_file}.xlsx',
                    file,
                    length=file_size,
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                logger.info(f'Upload file excel {name_file}.xlsx to Minio')
            except Exception as e:
                logger.error(e)
    else:
        logger.error(f"Path {file_path} not exist")