import argparse
import base64
import sys
import pyperclip
import os
import argparse

VALID_EXTENSIONS = [".pdf", ".docx", ".txt", ".xlsx", ".pptx"]

def list_documents(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: folder '{folder_path}' doesn't exist'")
        return []

    # list documents filtering by extension
    documents = [f for f in os.listdir(folder_path)
                 if os.path.isfile(os.path.join(folder_path, f)) and
                 os.path.splitext(f)[1].lower() in VALID_EXTENSIONS]

    # show list with numbers
    if not documents:
        print("No documents found in folder")
        return []

    print("\nFound documents:")
    for i, doc in enumerate(documents, start=1):
        print(f"{i}. {doc}")

    return documents


def convert_to_base64(file_path):
    with open(file_path, "rb") as f:
        content = f.read()

    # convert to base64
    content_base64 = base64.b64encode(content).decode("utf-8")

    # copy to paperclyp
    pyperclip.copy(content_base64)
    print("base64 content has been copied to your paperclip")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Lists documents in a folder and copies the selected file as base64 to the clipboard")
    parser.add_argument(
        "folder",
        nargs="?",
        default=os.getcwd(),
        help="Path to the folder containing documents (default: current working directory)"
    )
    args = parser.parse_args(argv)

    folder_path = args.folder
    documents = list_documents(folder_path)

    if documents:
        try:
            select = int(input("\n Enter a document's number to convert: "))
            if 1 <= select <= len(documents):
                selected_file = documents[select - 1]
                file_path = os.path.join(folder_path, selected_file)
                convert_to_base64(file_path)
            else:
                print("Number out of range")
        except ValueError:
            print("Entry isn't valid. You have to enter a number")


if __name__ == "__main__":
    main()