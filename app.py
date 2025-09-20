from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from google.cloud import documentai_v1 as documentai
import html

app = FastAPI(title="Trade Extractor OCR Service")

# TODO: Replace with your own GCP Document AI project details
PROJECT_ID = "YOUR_PROJECT_ID"
LOCATION = "YOUR_PROCESSOR_LOCATION"  # e.g., "us"
PROCESSOR_ID = "YOUR_PROCESSOR_ID"

@app.get("/", response_class=HTMLResponse)
async def main():
    return """
    <html>
        <head>
            <title>Trade Extractor OCR Service</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f2f2f2; }
                h2 { color: #333; }
                form { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                input[type=file] { margin-bottom: 10px; }
                input[type=submit] { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
                input[type=submit]:hover { background-color: #45a049; }
                .result { margin-top: 30px; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); white-space: pre-wrap; word-wrap: break-word; max-height: 500px; overflow-y: scroll; }
                .filename { font-weight: bold; margin-bottom: 10px; }
                .logo { max-height: 100px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <img src="assets/logo.png" alt="TradeGuard Logo" class="logo"/>
            <h2>Upload a file for OCR</h2>
            <form action="/upload" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff"/><br>
                <input type="submit" value="Upload & Extract Text">
            </form>
        </body>
    </html>
    """

@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    file_content = await file.read()
    client = documentai.DocumentProcessorServiceClient()
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"

    document = {"content": file_content, "mime_type": file.content_type}
    request = {"name": name, "raw_document": document}

    try:
        result = client.process_document(request=request)
        extracted_text = result.document.text
    except Exception as e:
        return f"<h3>Error:</h3><p>{html.escape(str(e))}</p>"

    safe_text = html.escape(extracted_text)

    return f"""
    <html>
        <head>
            <title>OCR Result</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f2f2f2; }}
                .result {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); white-space: pre-wrap; word-wrap: break-word; max-height: 500px; overflow-y: scroll; }}
                .filename {{ font-weight: bold; margin-bottom: 10px; }}
                a.button {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; }}
                a.button:hover {{ background-color: #45a049; }}
            </style>
        </head>
        <body>
            <h2>OCR Result</h2>
            <div class="result">
                <div class="filename">File: {html.escape(file.filename)}</div>
                <div>{safe_text}</div>
            </div>
            <a href="/" class="button">Upload Another File</a>
        </body>
    </html>
    """
