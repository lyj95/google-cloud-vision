"""OCR with PDF/TIFF as source files on GCS"""
import sys
from google.cloud import vision

# gcs_source_uri의 파일을 읽어와서 텍스트 추출하여 gcs_destination_uri에 JSON형식으로 저장
def async_detect_document(gcs_source_uri, gcs_destination_uri):
    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = 'application/pdf'

    # How many pages should be grouped into each json output file.
    # page 단위로 저장할 수 있다. defalut 값은 20이다. 최대 100
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

    print('Waiting for the operation to finish.')
    
    operation.result(timeout=420)

# async_detect_document('gs://test_gcv_bucket/searchSystem.pdf', 'gs://test_result_bucket/sample_result_')   
def main(string1, string2) :
    print(string1)
    print(string2)
 
if __name__ == "__main__" :
    main(sys.argv[1], sys.argv[2])
