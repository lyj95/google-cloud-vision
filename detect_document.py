"""OCR with PDF/TIFF as source files on GCS"""
import json
import re
from google.cloud import vision
from google.cloud import storage
import time

# gcs_source_uri의 파일을 읽어와서 텍스트 추출하여 gcs_destination_uri에 JSON형식으로 저장
def async_detect_document(gcs_source_uri, gcs_destination_uri):
    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = 'application/pdf'

    # How many pages should be grouped into each json output file.
    # page 단위로 저장할 수 있다. defalut 값은 20이다.
    batch_size = 100

    client = vision.ImageAnnotatorClient()

    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)
        # gcs_destination=gcs_destination)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)

    operation = client.async_batch_annotate_files(
        requests=[async_request])

    print('operation :')
    print(operation)

    print('Waiting for the operation to finish.')
    # 실행 시간 체크
    start = time.time()
    
    operation.result(timeout=420)

    print(time.time()-start)

# gcs_destination_uri 파일을 읽어 첫번째 페이지를 콘솔에 출력
def write_text_detection(gcs_destination_uri):
    # 저장된 파일 체크
    # Once the request has completed and the output has been
    # written to GCS, we can list all the output files.
    storage_client = storage.Client()

    match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)

    bucket = storage_client.get_bucket(bucket_name)

    # List objects with the given prefix.
    blob_list = list(bucket.list_blobs(prefix=prefix))
    print('Output files:')
    for blob in blob_list:
        print(blob.name)

    # Process the first output file from GCS.
    # Since we specified batch_size=2, the first response contains
    # the first two pages of the input file.
    output = blob_list[0]

    json_string = output.download_as_string()
    response = json.loads(json_string)

    # The actual response for the first page of the input file.
    first_page_response = response['responses'][0]
    annotation = first_page_response['fullTextAnnotation']

    # Here we print the full text from the first page.
    # The response contains more information:
    # annotation/pages/blocks/paragraphs/words/symbols
    # including confidence scores and bounding boxes
    print('Full text:\n')
    print(annotation['text'])

# async_detect_document('gs://sample_document_ibricks/searchSystem.pdf', 'gs://test_result_ibricks/sample_result_')    
async_detect_document('gs://test_gcv_bucket/us2010.pdf', 'gs://test_result_bucket/us2010_result_')    