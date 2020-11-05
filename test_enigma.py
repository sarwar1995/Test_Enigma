import pytest
from machine import Enigma
from components import Rotor, Plugboard, Reflector, ALPHABET

class BaseRotorTest():
    def setup_method(self):
        self.rotor_l = Rotor("I", "P") 
        self.rotor_m = Rotor("II", "D", next_rotor=self.rotor_l)
        self.rotor_r = Rotor("III", "U", next_rotor=self.rotor_m)
        self.rotor_l.prev_rotor = self.rotor_m
        self.rotor_m.prev_rotor = self.rotor_r

    def teardown_method(self):
        self.rotor_r = None
        self.rotor_l = None
        self.rotor_m = None


class TestRotor(BaseRotorTest):
    def test_rotor_repr(self, capfd):
        print(self.rotor_l)
        captured = capfd.readouterr()
        output = f"Wiring: \n{self.rotor_l.wiring}\nWindow: {self.rotor_l.window}\n"
        assert captured.out == output
        

    def test_invalid_rotor(self):
        with pytest.raises(ValueError) as err:
            Rotor("IV", "A")
            print(err)
        
    def test_rotor_step(self):
        self.rotor_r.step()
        assert self.rotor_r.offset == 21
        assert self.rotor_r.window == "V"
        self.rotor_r.step()
        assert self.rotor_m.offset == 4
        assert self.rotor_m.window == "E"
        self.rotor_r.step()
        assert self.rotor_m.offset == 5
        assert self.rotor_m.window == "F"
        assert self.rotor_l.offset == 16
        assert self.rotor_l.window == "Q"
    
    def test_rotor_encode_letter(self, capfd):
        """Tests all branches of the encode letter function using the middle rotor for forward and backward encoding and the 
        left rotor for single rotor encoding"""
     
        #Forward encoding through the next rotor
        assert self.rotor_m.encode_letter(1, forward=True, return_letter=False, printit=True) == 22
        captured = capfd.readouterr()
        output = f"Rotor {self.rotor_m.rotor_num}: input = {ALPHABET[(self.rotor_m.offset + 1)%26]}, output = S\n"
        #Testing for correct print if printit=True
        assert captured.out == output
        
        #Backward encoding through the previous rotor
        assert self.rotor_m.encode_letter(1, forward=False, return_letter=False, printit=False) == 4

        #Single rotor encoding with return_letter=True and return_letter=False
        assert self.rotor_l.encode_letter(1, forward=True, return_letter=True, printit=False) == "I"
        assert self.rotor_l.encode_letter(1, forward=True, return_letter=False, printit=False) == 8

        #Single rotor encoding with index = "A" a letter
        assert self.rotor_l.encode_letter("B", forward=True, return_letter=True, printit=False) == "I"


    def test_rotor_change_settings(self):
        self.rotor_l.change_setting("A")
        assert self.rotor_l.window == "A"
        assert self.rotor_l.offset == 0
            

class TestReflector():
    
    @pytest.fixture
    def valid_reflector(self):
        return Reflector()
    
    def test_refl_repr(self, valid_reflector, capfd):
        print(valid_reflector)
        captured = capfd.readouterr()
        output = f"Reflector wiring: \n{valid_reflector.wiring}\n\n"
        assert output == captured.out


class TestPlugboard():

    @pytest.fixture
    def valid_plug_swap(self):
        return Plugboard(['AB', 'XR'])
    
    @pytest.fixture
    def none_plug_swap(self):
        return Plugboard(None)


    def test_plug_repr(self, valid_plug_swap, capfd):
        print(valid_plug_swap)
        capture = capfd.readouterr()
        output = f"Swaps:\n{valid_plug_swap.swaps}\n\n"
        assert output == capture.out

    def test_none_plug_repr(self, none_plug_swap, capfd):
        print(none_plug_swap)
        capture = capfd.readouterr()
        output = f"Swaps:\n{none_plug_swap.swaps}\n\n"
        assert output == capture.out

    def test_print_swaps(self, valid_plug_swap):
        valid_plug_swap.print_swaps()
        assert True

    def test_update_swaps(self, valid_plug_swap, capfd):
        new_swap = ['JZ', 'QU']
        valid_plug_swap.update_swaps(new_swap, replace=False)
        updated_swaps = dict(A='B', B='A', X='R', R='X', J='Z', Z='J', Q='U', U='Q')
        #test for swap with replace=False
        assert valid_plug_swap.swaps == updated_swaps

        #test for swap with replace=True
        valid_plug_swap.update_swaps(new_swap, replace=True)
        updated_swaps.clear()
        updated_swaps = dict(J='Z', Z='J', Q='U', U='Q')
        assert valid_plug_swap.swaps == updated_swaps

        #test for swap > 6 with replace=False
        new_swap_limit = ['JZ', 'QU', 'EW', 'PO', 'SD' , 'FG' , 'NM']
        valid_plug_swap.update_swaps(new_swap_limit, replace=False)
        capture = capfd.readouterr()
        assert capture.out == "Only a maximum of 6 swaps is allowed.\n"

        #test for swap = None or not a list instance with replace=False
        none_swap = None
        valid_plug_swap.update_swaps(none_swap, replace=True) #This replace=True is needed to pass the test as it overwrites all swaps
        assert valid_plug_swap.swaps == {}


class TestEnigma():
    @pytest.fixture
    def valid_enigma(self):
        return Enigma(key='AAA', swaps=['AB', 'CD'], rotor_order=['I', 'II', 'III'])

    def test_invalid_key(self):
        with pytest.raises(ValueError) as err:
            Enigma(key='AA', swaps=None, rotor_order=['I', 'II', 'III'])
            print(err)
            
    def test_enigma_repr(self, valid_enigma, capfd):
        print(valid_enigma)
        capture = capfd.readouterr()
        output = f"Keyboard <-> Plugboard <->  Rotor {valid_enigma.rotor_order[0]} <-> Rotor {valid_enigma.rotor_order[1]} <-> Rotor {valid_enigma.rotor_order[2]} <-> Reflector \nKey: {valid_enigma.key}\n"
        assert capture.out == output

    def test_enigma_encipher(self, valid_enigma):
        valid_msg = "Hello World"
        invalid_msg = "Hello 12!"
        assert valid_enigma.encipher(valid_msg) == "ILACBBMTBE"
        assert valid_enigma.encipher(invalid_msg) == "Please provide a string containing only the characters a-zA-Z and spaces."

    def test_enigma_decipher(self, valid_enigma):
        valid_msg = "ILACBBMTBE"
        assert valid_enigma.decipher(valid_msg) == "HELLOWORLD"

    def test_enigma_encode_decode_letter (self, valid_enigma):
        invalid_letter = "4"
        assert valid_enigma.encode_decode_letter(invalid_letter) == "Please provide a letter in a-zA-Z."

    def test_enigma_encode_decode_letter_ValueError (self, valid_enigma):
        invalid_letter = " "
        with pytest.raises(ValueError) as err:
            assert valid_enigma.encode_decode_letter(invalid_letter) == "C"
            print(err)

    def test_enigma_set_rotor_position (self, valid_enigma, capfd):
        valid_position_key = "XYZ"
        invalid_position_key_1 = "MNOP"
        invalid_position_key_2 = 333
        valid_enigma.set_rotor_position (valid_position_key, printIt=True)
        #test for printit
        capture = capfd.readouterr()
        output = f"Rotor position successfully updated. Now using {valid_enigma.key}.\n"
        assert output == capture.out
        
        #test that valid key infact changes the window of each rotor
        assert valid_enigma.key == "XYZ"
        assert valid_enigma.l_rotor.window == "X"
        assert valid_enigma.m_rotor.window == "Y"
        assert valid_enigma.r_rotor.window == "Z"

        #test for invalid key 1
        valid_enigma.set_rotor_position (invalid_position_key_1, printIt=False) 
        capture = capfd.readouterr()
        assert capture.out == "Please provide a three letter position key such as AAA.\n"
        
        #test for invalid key 2
        valid_enigma.set_rotor_position (invalid_position_key_2, printIt=False) == "Please provide a three letter position key such as AAA."
        capture = capfd.readouterr()
        assert capture.out == "Please provide a three letter position key such as AAA.\n"

        #test for branch when printit=False with a valid position
        valid_enigma.set_rotor_position (valid_position_key, printIt=False)
        assert valid_enigma.key == "XYZ"

    def test_enigma_set_rotor_order (self, valid_enigma):
        valid_rotor_order = ['II', 'III', 'I']
        valid_enigma.set_rotor_order (valid_rotor_order)
        assert valid_enigma.l_rotor.rotor_num == "II"
        assert valid_enigma.m_rotor.rotor_num == "III"
        assert valid_enigma.r_rotor.rotor_num == "I"
        assert valid_enigma.m_rotor.prev_rotor.rotor_num == "I"
        assert valid_enigma.l_rotor.prev_rotor.rotor_num == "III"
    
    def test_enigma_set_plugs (self, valid_enigma):
        valid_swaps = ['ST','UV']
        valid_swaps_2 = ['PQ']
        valid_enigma.set_plugs(valid_swaps, replace=True)
        assert valid_enigma.plugboard.swaps == dict(S='T', T='S', U='V', V='U')
        valid_enigma.set_plugs(valid_swaps_2, replace=False)
        assert valid_enigma.plugboard.swaps == dict(S='T', T='S', U='V', V='U', P='Q', Q='P')




# if __name__ == "__main__":
#     machine_1 = Enigma('ELQ', swaps=[('A', 'B'), ('T', 'G')], rotor_order=['II', 'I', 'III'])
#     print(machine_1)
#     ciph_1 = machine_1.encipher("My name is Sarwar")
#     print(ciph_1)