# Purpose

Creating and sharing documents on Google Drive to collect students
homework for grading.

# Command Line Parameters

* `-p` or `--prefix`: a mnemonic prefix that will start the name of the document for the student (e.g., `cmputXYZ-wTT-hwN`)
* `-f` or `--folder`: the name of the folder in drive where the documents are stored
* `-s` or `--students`: JSON file with three fields per student: name, email, and id, which are used to name the document


Sample JSON file with student list:

```
[
  {"name": "Wonderland, Alice", "email": "alice@wonderland", "id": "123"},
  {"name": "Builder, Bob", "email": "bob@builder", "id": "234"}
]
```

# Initial Setup

1. Enable the Drive API for the institutional account used on the course (follow the [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python))
2. Download the credentials and put them on the same folder as the script.

# Naming of Folders and Documents

Folders and files on Google Drive are accessed via internal identifiers (instead of paths). The program first searches for a directory (anywhere) in the Google Drive corresponding to the provided access token matching the parameter `folder`.

If the folder is found, the program creates a blank document for each student listed in the student file, naming each file with the prefix (so that the student knows what the document is about) followed by the student name and the provided student id in parenthesis.

Example:
```
python create_and_share_google_docs.py -f cmput391w19hw1 -p "cmput391 w19 hw1" -s students.json
```

Would create documents `cmput391 w19 hw1 - Wonderland, Alice (123)` and `cmput391 w19 hw1 - Builder, Bob (s34)` inside folder with name **cmput391w19hw1**.

It might be best to test everything with an empty student file.

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
