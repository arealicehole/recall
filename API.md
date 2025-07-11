# Recall API Documentation

This document provides a detailed guide for integrating with the Recall application's web API. The API allows you to upload audio files, manage transcription jobs, and retrieve transcript data for further processing.

## Base URL

All API endpoints are relative to the base URL where the application is hosted. For example, if the application is running on `http://localhost:5000`, the full URL for the status endpoint would be `http://localhost:5000/api/status`.

## Authentication

The API itself does not require an authentication token for its endpoints. However, a valid **AssemblyAI API key** must be configured on the server for the transcription functionality to work. You can configure this key via the `POST /api/config` endpoint.

---

## Core Workflow

The primary workflow for processing an audio file involves these steps:

1.  **Upload Audio:** Send a `POST` request to `/api/upload` with your audio file(s) to start a new transcription job.
2.  **Check Status:** Poll the `GET /api/job/{job_id}` endpoint to monitor the job's progress.
3.  **Retrieve Transcript:** Once the job is complete, fetch the structured JSON transcript from `GET /api/transcript/{job_id}/{filename}`.
4.  **Submit Processed Data:** After your external service has processed the transcript, send the results back to `POST /api/job/{job_id}/{filename}/processed`.

---

## Endpoints

### 1. System Status & Configuration

#### `GET /api/status`

Checks the operational status of the API.

-   **Method:** `GET`
-   **Success Response (200):**
    ```json
    {
      "api_key_configured": true,
      "status": "ok",
      "timestamp": "2023-10-27T10:00:00.123456"
    }
    ```

#### `GET /api/config`

Retrieves the current server configuration.

-   **Method:** `GET`
-   **Success Response (200):**
    ```json
    {
      "api_key_configured": true,
      "output_directory": "transcripts"
    }
    ```

#### `POST /api/config`

Sets the AssemblyAI API key.

-   **Method:** `POST`
-   **Body (JSON):**
    ```json
    {
      "api_key": "YOUR_ASSEMBLYAI_API_KEY"
    }
    ```
-   **Success Response (200):**
    ```json
    {
      "success": true
    }
    ```

---

### 2. Transcription Jobs

#### `POST /api/upload`

Uploads one or more audio files to start a transcription job. This is a `multipart/form-data` request.

-   **Method:** `POST`
-   **Form Data:**
    -   `files`: The audio file(s) to transcribe. You can include multiple `files` fields.
    -   `output_directory` (optional): The directory where transcripts will be saved. Defaults to `transcripts`.
    -   `same_as_input` (optional): `true` or `false`. If `true`, transcripts are saved in the same directory as the source audio.
-   **Success Response (200):**
    ```json
    {
      "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "files_count": 1,
      "status": "started"
    }
    ```
-   **Error Response (400):**
    ```json
    {
      "error": "No files provided"
    }
    ```

#### `GET /api/jobs`

Lists all transcription jobs that have been created.

-   **Method:** `GET`
-   **Success Response (200):** An array of job objects.
    ```json
    [
      {
        "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "status": "completed",
        "progress": 100,
        "files_count": 1,
        /* ... other job details ... */
      }
    ]
    ```

#### `GET /api/job/{job_id}`

Retrieves the status and results of a specific transcription job.

-   **Method:** `GET`
-   **URL Params:**
    -   `job_id` (required): The UUID of the job.
-   **Success Response (200):**
    ```json
    {
      "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "status": "completed",
      "progress": 100,
      "current_file": "",
      "results": [
        {
          "file": "my_audio.wav",
          "status": "completed",
          "transcript_path_json": "uploads/a1b2.../my_audio_transcription.json",
          "transcript_preview": "Speaker A: Hello world..."
        }
      ],
      "error": null,
      "start_time": "2023-10-27T10:00:01.123456",
      "end_time": "2023-10-27T10:00:30.123456"
    }
    ```
-   **Error Response (404):**
    ```json
    {
      "error": "Job not found"
    }
    ```

---

### 3. Transcript Data

#### `GET /api/transcript/{job_id}/{filename}`

Downloads the full, structured JSON transcript for a specific file within a job.

-   **Method:** `GET`
-   **URL Params:**
    -   `job_id` (required): The UUID of the job.
    -   `filename` (required): The original name of the audio file.
-   **Success Response (200):** The raw JSON file is returned.
-   **Error Response (404):**
    ```json
    {
      "error": "Transcript file not found on disk"
    }
    ```

#### `POST /api/job/{job_id}/{original_filename}/processed`

Receives and saves a processed version of a transcript from an external service.

-   **Method:** `POST`
-   **URL Params:**
    -   `job_id` (required): The UUID of the job.
    -   `original_filename` (required): The original name of the audio file.
-   **Body (JSON):** Your custom processed JSON data.
    ```json
    {
      "summary": "This is a summary of the transcript.",
      "action_items": ["Follow up with team."]
    }
    ```
-   **Success Response (200):**
    ```json
    {
      "status": "success",
      "message": "Processed transcript saved to uploads/a1b2.../my_audio_transcription.processed.json"
    }
    ```
-   **Error Response (400/404/500):**
    ```json
    {
      "error": "No JSON data provided"
    }
    ```

#### `GET /api/download/{job_id}`

Downloads all completed transcripts from a job as a single `.zip` file.

-   **Method:** `GET`
-   **URL Params:**
    -   `job_id` (required): The UUID of the job.
-   **Success Response (200):** A zip file (`recall_transcripts_{job_id}.zip`) containing all transcript `.json` files.
-   **Error Response (404):**
    ```json
    {
      "error": "Job not found"
    }
    ``` 