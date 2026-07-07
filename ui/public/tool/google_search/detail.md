## Overview

Google Search is a real-time API tool for retrieving search engine results and structured data from Google. It supports multiple search types, including web, image, news, and maps.

## Configuration

1. Create a Google Custom Search Engine.
   Go to [Programmable Search Engine](https://programmablesearchengine.google.com/) and add a search engine.
   ![Create search engine](/admin/tool/img/google_AddSearchEngine.jpg)
2. Get the `cx` value.
   Open the engine details and copy the Search Engine ID from the **Basic** section.
   ![Get cx](/admin/tool/img/google_cx.jpg)
3. Get an API key.
   Open https://developers.google.com/custom-search/v1/overview?hl=en and create an API key.
   ![Get API key](/admin/tool/img/google_APIKey.jpg)
4. Configure startup parameters.
   Fill in the required parameters in the Google Search function startup settings and enable the function.
   ![Startup parameters](/admin/tool/img/google_setting.jpg)
5. Use in an application.
   In an advanced orchestration app, go to **Add Component -> Function Library -> Google Search** and configure parameters.
   ![Use in app](/admin/tool/img/google_app_used.jpg)
