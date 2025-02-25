
import zipfile
from io import BytesIO
from bs4 import BeautifulSoup

def get_shakespeare_data(
		url: str = "https://github.com/TheMITTech/shakespeare/zipball/master",
		pattern: str = "**/full.html",
        data_temp: Path|str = "../data/shakespeare_data",
		strip_html: bool = True,
		chars_threshold: int|None = None,
	) -> dict[str, str]:
    
	data_temp = Path(data_temp)
	data_cache: Path = data_temp / "processed.json"

	# read from cache if it exists
	if data_cache.exists():
		print(f"Reading from cache...")
		with open(data_cache, 'r', encoding='utf-8') as file:
			data: dict[str,str] = json.load(file)
		print(f"Read {len(data)} files from cache with {sum(len(v) for v in data.values())} characters")
		return data

	# Download the zip file
	print(f"Downloading repo...")
	response = requests.get(url)
	response.raise_for_status()  # Ensure that the download was successful	

	# Extract the zip file into a temporary directory
	print(f"Extracting zip file...")
	with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
		zip_ref.extractall(data_temp)

	# Find all 'full.html' files
	full_html_files = list(data_temp.glob(pattern))

	# Read contents of each 'full.html' file
	data: dict[str, str] = dict()
	# open each file
	print(f"Reading files...\n")
	chars_count: int = 0
	for file_path in full_html_files:
		print(f"\t{file_path.as_posix()}")
		with open(file_path, 'r', encoding='utf-8') as file:
			# read the raw html
			content: str = file.read()

			# turn it into plain text if requested
			if strip_html:
				soup: BeautifulSoup = BeautifulSoup(content, 'html.parser')
				content = soup.get_text(separator=' ', strip=True)

			# store it in the dictionary
			data[file_path.as_posix()] = content

			chars_count += len(content)
			print(f"\t\t{chars_count} characters read")
			if chars_threshold is not None and chars_count > chars_threshold:
				break
	
	# save to cache
	print(f"Saving to cache...")
	with open(data_cache, 'w', encoding='utf-8') as file:
		json.dump(data, file, indent=4)

	return data