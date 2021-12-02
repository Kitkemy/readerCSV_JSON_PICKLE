import sys
import json
import csv
import pickle

class FileReaderBase:

    ALLOWED_EXTENSIONS = (
        'json',
        'csv',
        'pickle'
        )

    def __init__(self, filename, output_filename, changes=[] ,path='',output_path=''):
        self.filename = filename
        self.path = path
        self.filetype = self.set_filetype()
        self.validated = self.validate()
        self.data = self.set_data()

        self.changes = changes
        self.change_requests = []
        self.output_filename = output_filename
        self.output_path = output_path
        self.output_filetype = self.set_output_filetype()



    def validate(self):
        if self.filetype not in self.ALLOWED_EXTENSIONS:
            print("nieobslugiwany format")
            return False
        return True

    def set_filetype(self):
        #return pathlib.Path(self.filename).sufix[:1]
        return self.filename.split(".")[-1]
    
    def get_filepath(self):
        if self.path:
            return f'{self.path}/{self.filename}'
        return self.filename

    def set_data(self):
        with open(self.get_filepath(), self.read_bytes()) as file:
            if hasattr(self, f'get_{self.filetype}_data'):
                self.data = getattr(self, f'get_{self.filetype}_data')(file)
                #test: print(self.data)
            else:
                self.data = []
                print(f'wymagana implementacja metody: get_{self.filetype}_data na {self}')
            return self.data

    def requested_changes(self):
        for request in self.changes:
            requests = request.split(',')
            self.change_requests.append(requests)

    def change_maker(self):
        for change in self.change_requests:
            row = int(change[0])
            column = int(change[1])
            value = change[2]
            self.data[row][column] = value 

    def set_output_filetype(self):
        return self.filename.split(".")[-1]  

    def get_output_filepath(self):
        if self.output_path:
            return f'{self.output_path}/{self.output_filename}'
        return self.output_filename

    def save_data(self):
        with open (self.get_output_filepath(), self.write_bytes()) as file:
            if hasattr(self, f'save_{self.output_filetype}_data'):
                #test: print(self.data)
                return getattr(self, f'save_{self.output_filetype}_data')(file)
            print(f'Konieczna implementacjametody: save_{self.output_filetype}_data.')
            return []

    def write_bytes(self):
        if self.filetype == 'pickle':
            return 'wb'
        else:
            return 'w'

    def read_bytes(self):
        if self.filetype == 'pickle':
            return 'rb'
        else:
            return 'r'

    def starter(self):
        self.read_bytes()
        self.write_bytes()
        self.requested_changes()
        self.change_maker()
        self.save_data()





class CSVReader(FileReaderBase):
    
    '''
    #ta metode dzieki zastosowaniu getattr przenosze do klasy bazowej
    def open_file(self):
        with open(self.get_filepath()) as file:
            print(getattr(self, f'get_{self.filetype}_data')())
            #self.get_csv_data(file)
    '''        

    def get_csv_data(self, file):
        data = []
        for line in file.readlines():
           data.append(line.replace('\n', '').split(','))
        return data

    def save_csv_data(self, file):
        thewriter = csv.writer(file)
        for item in self.data:
            thewriter.writerow(item)


class JSONReader(FileReaderBase):
    
    def get_json_data(self, file):
        data = []
        
        content = file.read()
        json_data = json.loads(content)
        #print(type(json_data))

        for key, value in json_data.items():
            data.append([key,value])
        return data

    def save_json_data(self, file):
        json.dump(self.data, file, indent=4)

class PickleReader(FileReaderBase):

    def get_pickle_data(self, file):
        return pickle.load(file)
    
    def save_pickle_data(self, file):
        pickle.dump(self.data, file)





filename = sys.argv[1]
output_file = sys.argv[2]
change_requests = sys.argv[3:]

#python reader.py "input.json" "output.json" "0,0,zakopane" 
#rd = JSONReader(filename, output_file, change_requests)

#python reader.py "input.csv" "output.csv" "0,0,zakopane" 
rd = CSVReader(filename, output_file, change_requests)

#python reader.py "input.pickle" "output.pickle" "0,0,zakopane" 
#rd = PickleReader(filename, output_file, change_requests)

rd.starter()
