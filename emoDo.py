from os import system
import sys,re, base64,zlib


class ObfuscatedText:
	"""
		Class to handle different types of obfuscated text. 

		args:
		deObfuscatedText (str)
		obfuscatedText (str)
		delimiter (str)

	

	"""

	#character set of special characters in regex
	regexSpecialChars = re.compile(r'[!#$%^&*(),.?":{}|\[\]<>\\]')
	regexObfuscatedNum = re.compile(r'\( *([0-9]*\W)+')

	def __init__(self,deObfuscatedText="",obfuscationType="",delimiter=""):
		self.obfuscatedText = input("Copy and Paste the Obfuscated text here:\n").lower().strip('"')
		self.deObfuscatedText = deObfuscatedText
		self.delimiter = delimiter
		self.obfuscationType = obfuscationType
		self.urls = ""

		# Clear the screen after institutionalized 
		system('cls')


		

	def extract_urls(self):
		"""

			

		"""


		if("frombase64string" in self.obfuscatedText):
			self.base64_decode()


		while True:

			if(self.delimiter == ""):
				try:
					# attempt to find the delimiter used by searching a character set of common delimiters seen
					self.delimiter = re.search(r'[@,]http',self.deObfuscatedText).group()[0]
					
				except AttributeError:
					# If the delimiter is not in the above character set then an attribute error will be thrown. 
					# Print the de-obfuscated text for the users reference and then prompt the user to ID the appropriate delimiter 
					print(self.deObfuscatedText)
					self.delimiter = input("A delimiter for the URLs couldn't be found. Please enter the delimiter used to separate the embedded URLs:")

				
			try:
				
				urls = [url for url in self.deObfuscatedText.split("='") if self.delimiter in url][0].split(self.delimiter)

				for url in [(url.split("'.")[0]) for url in urls if 'http' in url]:
					#Replace the HTTP protocol with HXXP
					self.urls += "{:<}\n".format(re.sub('http','hxxp',url))


				break

			except IndexError:
				input("The provided delimiter of {} appears to be incorrect, press any-key to try again. ")
				self.delimiter = ""
				system('cls')

			except Exception:
				return Exception("Unable to perform URL Extract {}".format(self.delimiter))


	def string_substitute(self):
		"""De-obfuscates text that uses a string-building library where the obfuscated string is
		 represented by numbers representing the index value of each character in the string library."""
		stringLibrary = ""
		listCharacterIndex = []

		while True:


			try:
				# Extract the series of numbers representing the string library index value 
				obfuscatedNums = re.split(r'\W',ObfuscatedText.regexObfuscatedNum.search(self.obfuscatedText).group().strip()[1:-1])

				#If the numbers are preceded by a empty/null value, drop it before converting to int.
				if('' in obfuscatedNums):
					obfuscatedNums.pop(obfuscatedNums.index(''))
				
				listCharacterIndex = [int(num) for num in obfuscatedNums]

				#Get the highest index in order to find the library.
				librarySize = max(listCharacterIndex) + 1
				
				min_char =  re.search(r'set.\w+=',self.obfuscatedText).span()[1]
				max_char = librarySize +  re.search(r'set.\w+=',self.obfuscatedText).span()[1]
				
				stringLibrary = self.obfuscatedText[min_char:max_char]
				
				

			except Exception:
				system('cls')
				print("Unable to automatically de-obfuscate lets try it different way....\n\n")
				
				# Attempt manual de-obfuscation 
				obfuscatedText = input("Copy and paste below the series of numbers representing the obfuscated text below:\n").strip()
				listCharacterIndex = obfuscatedText.split(input("Enter the character delimiter used to separate the number values: "))
				stringLibrary = input("Copy and paste the string library used to obfuscate the text:\n")

				
			try:
				for c in listCharacterIndex:

					self.deObfuscatedText += stringLibrary[int(c)]

				break
			except IndexError:
				input("\n\nError! The obfuscated text contains a reference to a character outside the provided string library.\n\nThe referenced character was %s. Check the provided string library and obfuscated text and try again." % (c))
				
			except Exception:
				raise Exception
				input("The pasted text looks to be of a different obfuscation than expected. Press any key to try again.")



		self.obfuscationType = "String Substitute"

	def reverse_string(self):
		"""Reverses the string if it's reversed."""

		splitObfuscatedText = re.split(r'(=;)',self.obfuscatedText)
		self.deObfuscatedText = splitObfuscatedText[0] + '=;'+ splitObfuscatedText[2][::-1]
		self.obfuscationType = "Reverse String"
		return 


	def string_addition(self):
		"""
			Function is designed try and parse text that is string split by plus s
		
		"""


		if("-join" not in self.obfuscatedText):
			input("Provided obfuscated text is incompatible with the String Addition.\n Check the help to ensure you've selected the right type de-obfuscation type for your text.\nPress any key to return to the main menu")
			main()

		splitObfuscatedText = re.split(r'(\(\(|\) *\))',self.obfuscatedText)[2].split("'+'")

	
		for string in splitObfuscatedText:
			self.deObfuscatedText += string


		return self.deObfuscatedText


	def variable_substitute(self):
		"""
		De-obfuscates text that uses multiple variable declarations and find/replace statements. 
		this type of obfuscation can be identified by the multiple set varY=varX:find=Repl found near the end of the text.

		"""
		
		setRegex = re.compile('&+ *set (\w+=\!\w+\:(\w*\W*)=(\w*\W*)\!)')

		#Find all set statements with find-replace functions (Defined by set varY=varX:a=b)
		listSetReplacements = [(x[1],x[2]) for x in setRegex.findall(self.obfuscatedText)]

		#Split the obfuscated text between the list of set statements and the text containing the URLs
		splitObfuscatedText = re.split(r'(;)&+ set',self.obfuscatedText)[0]


		for patt in listSetReplacements:

			try:
				# Look for special characters in the pattern used for find/replace, escape the special character if one is found.
				#if(re.search(r'[!#$%^&*(),.?":{}|\[\]<>\\]',patt[0])!=None):
				if(ObfuscatedText.regexSpecialChars.search(patt[0])!=None):

					x = None
					# If the character is a special character in cmd, escape it using the ^
					if(re.search(r'[\%]',patt[0])!=None):
						x = re.compile('\^\%s' % patt[0])
					else:
						x = re.compile('\%s' % patt[0])
					splitObfuscatedText = x.sub(patt[1],splitObfuscatedText)
				else:
					x = re.compile('%s' % patt[0])
					splitObfuscatedText = x.sub(patt[1],splitObfuscatedText)

			except re.error:
				# Look for special characters in the pattern used for find/replace, escape the special character if one is found.
				if(re.search(r'[!#$%^&*(),.?":{}|\[\]<>\\]',patt[1])!=None):
					splitObfuscatedText = x.sub("\%s" % (patt[1]),splitObfuscatedText)
					

				else:
					input("An error occurred when de-obfuscating the following pattern:\n{},{}\nPartially de-obfuscated text:\n{}".format(patt[0],patt[1],splitObfuscatedText))
					

			except Exception as e:
				input("The pasted text looks to be of a different obfuscation than expected. Press any key to try again.")
				

	

		self.deObfuscatedText = splitObfuscatedText
		self.obfuscationType = "String Substitute"

	def __str__(self):
		
		system('cls')
		s = "OBFUSCATION TYPE: {:<}\n\nFOUND URLS:\n\n{:<}\n\nDEOBFUSCATED TEXT:\n\n{:<}".format(self.obfuscationType,self.urls,self.deObfuscatedText)

		return s

	def save_text(self):
		"""Gives the user the option of saving the de-obfuscated text. """
		if(input("\n\nSave output? Y/N ").lower()=='y'):
			while True:
				try:
					with open(input("Save File As: "),'w') as file:
						file.write(self.__str__())
						input("File Saved successfully...press any key to continue")
					main()
				except Exception as e:
					raise Exception
					input("Error writing to file. Check the name and try again. Press any key to continue")

def show_help():
	s = """
		String Library Builder: De-obfuscates text that uses a string-building library where the obfuscated string is
				represented by numbers representing the index value of each character in the string library.
		 
		Set Variable Substitute: De-obfuscates text that uses multiple variable declarations and find/replace statements. 
			this type of obfuscation can be identified by the multiple set varY=varX:find=Repl found near the end of the text. 

		Reverse String: Reverse a string.

		String Addtion: parse text that is string split by plus s

		Press Any Key to Return
	"""
	input(s)
	main()
	return s

def main():
	listMenuItems = ['String Library Builder','Set Variable Substitute','Reverse String', 'String Addition','Help']
	
	while True:
		try:
			system('cls')
			print("\nSelect the type of obfuscated text you wish to de-obfuscate: ")
			[print("{}: {}".format(i,item)) for i,item in enumerate(listMenuItems)]
			userInput = int(input("> "))
			obfText = ObfuscatedText()
			if('String Library Builder'==listMenuItems[userInput]):
				obfText.string_substitute()

			elif('Set Variable Substitute'==listMenuItems[userInput]):
				obfText.variable_substitute()

			elif("Reverse String"==listMenuItems[userInput]):
				obfText.reverse_string()

			elif("String Addition" == listMenuItems[userInput]):
				obfText.string_addition()

			elif("Help" == listMenuItems[userInput]):
				show_help()
				
			obfText.extract_urls()
			

			print(obfText)
				
			obfText.save_text()
			sys.exit(0)
		except ValueError:
			raise ValueError
			input("Invalid menu selection, press any key to try again.")

		except TypeError:
			raise TypeError
			input("Invalid menu selection, press any key to try again.")

		except Exception as e:
			raise e
			print("An Unknown error has occurred:\n")
			


	
if __name__ == '__main__':
	main()

