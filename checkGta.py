import hashlib
import os

# Configure this to the name of the install directory
gtaDirectory = r'C:\Games\GTAV'

# Initialize a list of files to ignore based on the install directory
ignoreFiles = ['commandline.txt',
               'GTA5.exe',
               'GTAVLauncher.exe',
               'PlayGTAV.exe',
               'ReadMe\Chinese\ReadMe.txt',
               'ReadMe\English\ReadMe.txt',
               'ReadMe\French\ReadMe.txt',
               'ReadMe\German\ReadMe.txt',
               'ReadMe\Italian\ReadMe.txt',
               'ReadMe\Japanese\ReadMe.txt',
               'ReadMe\Korean\ReadMe.txt',
               'ReadMe\Mexican\Readme.txt',
               'ReadMe\Polish\ReadMe.txt',
               'ReadMe\Portuguese\ReadMe.txt',
               'ReadMe\Russian\ReadMe.txt',
               'ReadMe\Spanish\ReadMe.txt']
ignoreList = []
for ignoreFile in ignoreFiles:
    ignoreList.append(os.path.join(gtaDirectory, ignoreFile))

# Initialize the log file, or clear it if it's present
logFile = os.path.expanduser('~\checkGta.log')
print(f'Logging all output to: {logFile}')
with open(logFile, 'w') as log:
    log.write('')

# Ingest the master hash list
hashList = {}
with open('hashes.txt', 'r') as hashFile:
    lineType = 0
    fileName = ''
    for line in hashFile:
        # Find the new line, if present
        newLineIndex = line.find('\n')
        if lineType == 0:
            # This line should be the file name, including subdirectories
            if newLineIndex > -1:
                fileName = os.path.join(gtaDirectory, line[:newLineIndex])
            else:
                fileName = os.path.join(gtaDirectory, line)
            lineType += 1
        elif lineType == 1:
            # Skip this line, only used for notes
            lineType += 1
        elif lineType == 2:
            # This line should be the file hash
            fileHash = -1
            if newLineIndex > -1:
                fileHash = line[:newLineIndex]
            else:
                fileHash = line
            hashList[fileName] = fileHash
            lineType = 0

# Setup some buckets for counting
okayFiles = 0
badFiles = 0
unknownFiles = 0

for dirpath, dirnames, filenames in os.walk(gtaDirectory):
    for filename in filenames:
        gtaFile = os.path.join(dirpath, filename)

        if gtaFile in hashList:
            # Hash this file
            BLOCKSIZE = 131072
            hasher = hashlib.sha256()
            with open(gtaFile, 'rb') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
            gtaHash = hasher.hexdigest()

            # Pull the hash for this file
            fileHash = hashList[gtaFile]
            if fileHash == gtaHash:
                status = f'{gtaFile} OK!'
                with open(logFile, 'a') as log:
                    log.write(status + '\n')
                print(status)
                okayFiles += 1

            else:
                status = f'{gtaFile} CORRUPT!'
                expected = f"Expected '{fileHash}' but found '{gtaHash}'"
                with open(logFile, 'a') as log:
                    log.write(status + '\n')
                    log.write(expected + '\n')
                print(status)
                print(expected)
                badFiles += 1

        elif gtaFile not in ignoreList and gtaFile.find('.part') == -1 and gtaFile.find('.hash') == -1:
            # Not sure about this file, output for inspection
            status = f'Unknown file: {gtaFile}'
            with open(logFile, 'a') as log:
                log.write(status + '\n')
            print(status)
            unknownFiles += 1

# All files processed, output results
print(f'{okayFiles} files OK, {badFiles} files CORRUPT, {unknownFiles} files unknown')

# Pause for the folks that double-click
enter = input('Press ENTER to complete the script...')
print('Script complete.')
