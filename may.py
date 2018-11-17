import os
import argparse
import re
import sys


INLINE_DOC_CHARS = 70

def iterated(func):
	def func_wrapper(*args, **kwargs):
		items = []
		for item in func(*args, **kwargs):
			items.append(item)
		return items
	return func_wrapper


@iterated
def get_import_names(base_path):
	"""Returns the name of all python modules that may be imported from the base folder
	
	This function returns the import names of python-module-alike. The function will consider
	importable any .py file and any folder, regarldess of whether they are importable or not.
	
	:param base_path: The path to do the search in
	:type base_path: str
	:return: List of importable names
	:rtype: list
	"""
	for item in os.listdir(base_path):
		# Skip the script manager files
		if item == "may.bat" or item == "may.py" or item == "__pycache__":
			continue
		# If the item is a python file, use its name (without .py) for import
		if os.path.isfile(os.path.join(base_path, item)):
			m = re.match("(.+)\.py", item)
			if m:
				yield m.group(1)
		# If the item is a folder, use its entire name for import
		else:
			yield item
			
			
def extract_doc_title(string):
	"""Extracts a correctly parsed doc title from a string
	
	:param string: The raw doc title
	:type string: str
	:return: The normalized doc title, with excess blank lines removed
	:rtype: str"""
	doc_title = string.split("===")[0]
	# If there is a title, strip out excess line returns
	if len(doc_title) > 0:
		if re.match("^\n", doc_title):
			doc_title = doc_title[1:]
		if doc_title[-1] == '\n':
			doc_title = doc_title[:-1]
	return doc_title
	

@iterated	
def get_quick_doc(names):
	"""Returns a list of module/script names paired with their documentation titles
	
	:param names: The names of importable modules
	:type names: list
	:return: A list of dictionaries, with name and title keywords
	:rtype: list
	"""
	for name in names:
		try:
			doc = __import__(name).__doc__
			yield {
				'name': name,
				'title': extract_doc_title(doc if doc else "")
			}
		except ModuleNotFoundError:
			pass

			
def multiple_lines(text, line_length):
	"""Splits text by space onto multiple lines of maximum required length
	
	:param text: The text to split on multiple lines
	:type text: str
	:param line_length: Max length allowed for each line
	:type line_length: int
	:return: Text split on multiple lines
	:rtype: list
	"""
	lines = []
	line = ""
	for word in text.split(" "):
		if line == "":
			candidate = word
		else:
			candidate = line + " " + word
		if len(candidate) < line_length:
			line = candidate
		else:
			lines.append(line)
			line = word
	if len(line) > 0:
		lines.append(line)
	if len(lines) == 0:
		lines.append("")
	return lines
	
def longest_text(text_list):
	"""Returns the length of the longer text in a list
	
	:param text_list: List of texts to measure
	:type text_list: list
	:return: The length of the longer text in the list
	:rtype: int
	"""
	max_length = 0
	for text in text_list:
		if len(text) > max_length:
			max_length = len(text)
	return max_length

def adjusted_legth_text(text, length):
	"""Returns a text padded with spaces on the right to match a length
	
	:param text: Text to pad
	:type text: str
	:param length: Desired length with padding
	:type length: int
	:return: Padded text
	:rtype: int
	"""
	if len(text) < length:
		return text + "".join([" " for _ in range(length - len(text))])
	return text
	
	
def available_scripts():
	"""Returns the list of available scripts, ready to be printed
	
	:return: The available scripts with quick documentation
	:rtype: str
	"""
	script_names = get_import_names(os.path.dirname(os.path.realpath(__file__)))
	max_length = longest_text(script_names)
	data = get_quick_doc(script_names)
	res = ""
	for item in data:
		for i, line in enumerate(multiple_lines(item['title'], INLINE_DOC_CHARS)):
			if i == 0:
				res += " {}\t{}\n".format(adjusted_legth_text(item['name'], max_length), line)
			else:
				res += " {}\t{}\n".format(adjusted_legth_text('', max_length), line)
	return res


def general_help():
	"""Returns the general help with the list of available scripts
	
	:return: The help message ready to print
	:rtype: str
	"""
	return """This tool is a generic script manager that acts as a controller of scripts of different
kinds.
 may <script name> --help	Quick help and parameters description
 may manual <script name>	Read the full manual of this script
	
Below, a list of the available scripts:

{}

""".format(available_scripts())
	
	
def main():
	# No extra keyword, print general help
	if len(sys.argv) <= 1:
		print(general_help())
	# Extra keywords, can be may parameters or script parameters
	else:
		# Asking for the manual
		if sys.argv[1] == "manual" and len(sys.argv) == 3:
			try:
				doc = __import__(sys.argv[2]).__doc__
				print(doc if doc else "")
			except ModuleNotFoundError:
				print("ERROR: Script not found")
		# When all previous check fails, we are calling a script
		else:
			try:
				# Remove "may" and script name
				args = sys.argv[2:]
				__import__(sys.argv[1]).main(args)
			except ModuleNotFoundError:
				print("ERROR: Script not found")
if __name__ == "__main__":
	main()