import os

root = os.getcwd()
doc_directory = root+'/docs'
if not os.path.exists(doc_directory):
    os.mkdir(doc_directory)
    os.mkdir(doc_directory+'/qa_tests')
