from typing import Dict
from multiprocessing import Process, Queue
from queue import Empty

from serial import Serial

from drivers.serial_protocol import receive_message, construct_message

LIVE_DATA_SAMPLE = b'\x18\x0e\x00\x00\x00\x00\x00\x00\x00\x00y*y*\xe4Q\xe4Q&\x00\x18\xe7' \
                   b'\x04+\x02k\x02f\x00\xe2\x00N\x07\xfc\x03\x00\x00\xe8\x03\xe8\x03\xe8\x03\xe8\x03\xdc\x03\xdc' \
                   b'\x03\x00\x90\x00\x019\xb4kn\x02\xe4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                   b'\x00\x00\x002\x00\x1d\x00\x00\x00\x00S\x00A\x01\xf4\xc6\x00\x00\x00\x00\x00\x00\x00\x00\x00' \
                   b'\xffr\xff\xb3s\x18\x9b\x9a\x01O\n^\x00\x00\xb4k\xff\x9a\x00\x00K\x96R\x0c\x04\x0c\x04\x00'


class Ecm:
    def __init__(self, serial_port: str, live_data_dict: dict, mock=False):
        """
        :param serial_port: passed through to the serial.Serial constructor
        :param live_data_dict: a dictionary containing info about all the available live data like location and format
        :param mock: If set to true, the ECM's data is not requested and some old data I have lying around is used
        """
        self.serial_port_str = serial_port
        self.live_data_dict = live_data_dict
        self.mock = mock
        self.conn = None

        self.__poll_process = None
        self.__queue = Queue()
        self.__cached_live_data = None

    def open_conn(self):
        if self.conn:
            self.conn.close()

        if not self.mock:
            self.conn = Serial(self.serial_port_str, timeout=0.1)

    def close_conn(self):
        if self.conn:
            self.conn.close()

    def begin_poll(self):
        """Sets up a subprocess that makes sure that the latest live data is automatically available"""
        self.open_conn()

        def poll():
            while True:
                data = self.__fetch_live_data()
                try:
                    self.__queue.get_nowait()
                except Empty:
                    pass

                self.__queue.put(data)

        self.__poll_process = Process(target=poll)
        self.__poll_process.start()

    def end_poll(self):
        """Ends the process set up by begin_poll"""
        self.close_conn()

        if self.__poll_process:
            self.__poll_process.terminate()
            self.__poll_process.join()
            self.__poll_process = None

    @property
    def live_data(self) -> dict:
        """
        :return: the live data from the ECM as a dictionary where the key is a key from the live data dictionary
            and the value is the value of that datum.

        This will be much quicker if begin_poll() and end_poll() are used.
        """

        if self.__poll_process:
            try:
                latest_data = self.__queue.get_nowait()
                self.__cached_live_data = latest_data
                return latest_data
            except Empty:
                if self.__cached_live_data:
                    return self.__cached_live_data

        return self.__fetch_live_data()

    def __fetch_live_data(self) -> dict:
        """
        Requests the live data from the ECM and returns all of the data therein parsed and formatted as a dictionary.
        """
        if self.mock:
            live_data = LIVE_DATA_SAMPLE
        else:
            self.conn.write(construct_message(b'C'))
            live_data = receive_message(self.conn)

        out = {}
        for param_name, param_info in self.live_data_dict.items():
            if param_info['type'] == 'scalar':
                out[param_name] = self.__parse_scalar(live_data, param_name)
            else:
                out[param_name] = self.__parse_bitfield(live_data, param_name)

        return out

    def __parse_scalar(self, live_data: bytes, name: str) -> float:
        """
        Pulls the given scalar parameter out of the live data buffer and returns it as a float

        :param live_data: the full live data buffer
        :param name: the name of the scalar parameter
        :return: the parameter's value as a float
        """
        param_data = self.__get_parameter_data(live_data, name)
        param_info = self.live_data_dict[name]

        if param_info['type'] != 'scalar':
            raise ValueError(f'{name} is not a scalar parameter')

        value = int.from_bytes(param_data, param_info['endianness'], signed=param_info['signed'])
        value *= param_info['scale_factor']
        value += param_info['offset']

        return float(value)

    def __parse_bitfield(self, live_data: bytes, name: str) -> Dict[str, bool]:
        """
        Pulls the values of the given bitfield out of the live data buffer

        :param live_data: the full live data buffer
        :param name: the name of the bitfield
        :return: a dictionary where the key is the name of the bit and the value is the bit converted to a bool
        """
        param_data = self.__get_parameter_data(live_data, name)
        param_info = self.live_data_dict[name]

        if param_info['type'] != 'bitfield':
            raise ValueError(f'{name} is not a bitfield parameter')

        param_data = int.from_bytes(param_data, 'big')

        out = {}
        for bit_idx, bit_description in enumerate(param_info['bits']):
            bit_value = (param_data >> bit_idx) & 1
            out[bit_description] = bool(bit_value)

        return out

    def __get_parameter_data(self, live_data: bytes, parameter_name: str) -> bytes:
        """
        Iterates over the addresses of the given parameter and puts together all the data for that parameter

        :param live_data: the full live data buffer
        :param parameter_name: the name of the bitfield or scalar parameter
        :return: all of the bytes data for the given parameter
        """
        out = b''
        for location in self.live_data_dict[parameter_name]['addresses']:
            out += live_data[location['offset']: location['offset'] + location['num_bytes']]

        return out

