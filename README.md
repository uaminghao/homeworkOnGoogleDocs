# Purpose

Creating and sharing documents on Google Drive to collect students
homework for grading.

# Command Line Parameters

* `-c` or `--course`: a course code, used as a prefix for the documents **and also** as part of the name of the folder where the documents will be created
* `-hw` or `--howmeork`: the homework name, also used as part of the document names and the folder name
* `-s` or `--students`: JSON file with three fields per student: name, email, and id, which are used to name the document
* `-t` or `--token`: JSON file with the credentials

Sample JSON file:

```
[
  {"name": "Wonderland, Alice", "email": "alice@wonderland", "id": "123"},
  {"name": "Builder, Bob", "email": "bob@builder", "id": "234"}
]
```

# Naming of Folders and Documents

Folders and files on Google Drive are accessed via internal identifiers (instead of paths). The code first searches for a directory (anywhere) in the Google Drive whose name is the concatenation of the course prefix and the homework name, separated by a space. If no such folder exists, the program exits.

If the folder is found, the program creates a blank document for each student in the student file, naming each file with the folder name (so that the student knows what the document is about) followed by the student name and the provided student id in parenthesis.

Example:
```
python create_and_share_google_docs.py -c cmput391f18 -hw "homework 1" -t token.json -s students.json
```

Would create the following documents with the students as in the JSON file above: **cmput391f18 homwork 1 Wonderland, Alice (123)**, and **cmput391f18 homwork 1 Builder, Bob (234)** inside a folder called **cmput391f18 homwork 1** (anywhere in the drive).


# Initial Setup

1. Enable the Drive API (follow the [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python))
2. Run the code from the command line and authenticate to the account that will own the documents (e.g., an institutional account for the course)

After these steps there should be a JSON file, named as indicated by the `-t` parameter, with the credentials needed by the API. It might be best to do the setup with an empty student file.


### Legal

This code wad produced by modifying the [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python).

Copyright 2018 Denilson Barbosa

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.