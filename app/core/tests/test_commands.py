"""
Test custom Django management commands
"""

from unittest.mock import patch # import patch to mock behavior of the database because we need to simulate database returning a response or not.

from psycopg2 import OperationalError as Psycopg2Error # One of the errors that we might get when try and connect to the database before the database is ready.

from django.core.management import call_command # a helper function provided by Django that allows us to simulate or actually call a command by the name -> allows us to actually call the command that we're testing
from django.db.utils import OperationalError # another operational error, with is another exception that may get thrown by the database depending on what stage of the start up process it is -> basically want to cover both options
from django.test import SimpleTestCase

"""
* Chi tiết về @patch
Câu lệnh @patch('core.management.commands.wait_for_db.Command.check') đang làm những điều sau đây:
+ Nhắm tới đối tượng cần mock:
- 'core.management.commands.wait_for_db.Command.check' là chuỗi đại diện cho đường dẫn đến đối tượng mà bạn muốn mock. Trong trường hợp này, bạn đang mock phương thức check của lớp Command nằm trong file wait_for_db.py trong thư mục commands của ứng dụng core.
+ Thay thế đối tượng bằng mock object:
- @patch sẽ thay thế đối tượng check bằng một mock object trong suốt thời gian thực thi của hàm kiểm tra.
+ Cung cấp mock object cho hàm kiểm tra:
- Mock object này được truyền vào hàm kiểm tra dưới dạng tham số (patched_check trong trường hợp này).

* Mocking Object
+ Mocking object trong đoạn mã này chính là patched_check. patched_check là một mock object được tạo ra và quản lý bởi unittest.mock.patch. Bạn có thể tùy chỉnh hành vi của patched_check để kiểm tra các tình huống khác nhau.
+ Các bước hoạt động
- Tạo mock object: @patch('core.management.commands.wait_for_db.Command.check') tạo ra một mock object và thay thế phương thức check bằng mock này.
- Truyền mock object: patched_check được truyền vào các phương thức kiểm tra như một tham số.
- Tùy chỉnh hành vi của mock object: Trong test_wait_for_db_ready, bạn đặt patched_check.return_value = True để giả lập tình huống cơ sở dữ liệu sẵn sàng.
Trong test_wait_for_db_delay, bạn đặt patched_check.side_effect để giả lập các ngoại lệ khác nhau và cuối cùng là trả về True.
"""
@patch('core.management.commands.wait_for_db.Command.check') 
# core.management.commands.wait_for_db.Command.check is the command that we're going to be mocking -> we're going to mocking that check method to simulate the response -> so we can simulate that check method -> returning an exeption, authorizing an exception and we can also simulate it.
# use unittest.mock.patch to simulate behavior of check method in Command class
class CommandTests(SimpleTestCase):
    """Test commands."""

    # Test Case 1 -> Testing what happens when the database ready
    def test_wait_for_db_ready(self, patched_check): # patched_check object: the magic object is replace by @patch('core.management.commands.wait_for_db.Command.check') (return wrapped_function(patched_check=RETURN_OBJECT)) -> we can use patched_check to customize the behavior
        """Test waiting for database if database ready."""
        patched_check.return_value = True # when we call check or when check is called inside our command, inside our test case, we just want it to return the true value

        call_command('wait_for_db') # actually execute the code inside wait_for_db

        """
        This kind of test, two things:
        + The situation where the database is ready and we run the command
        + Also check that the commands is set up correctly and can be called inside our Django project
        """

        patched_check.assert_called_once_with(databases=['default']) # ensures that the "mock value, the mocked object, the check method" inside our command is called with these parameters. 
        # call once time

    # Test Case 2 -> Testing what happens or what should happen if the database isn't ready.
    # This mean the database returns some exceptions or the check method returns some exceptions that indicate that the databse isn't ready yet.
    @patch('time.sleep') # We don't want to wait in the tests so we don't want to actually wait in our unittest because this just going to slow our test down 
    def test_wait_for_db_delay(self, patched_sleep, patched_check): # when there's a delay in starting, we want to simply check if the database is ready, the database isn't ready -> so we want it to delay a few senconds and try again -> match with patched_sleep
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True] 
        # for the second test, we want it to actually raise some exeptions that would be raised if the database wasn't ready.
        # so the way that you make it raise an exception instead of actually pretend to get value (Test Case 1) is use side_effect. So the side_effect allows you to pass in various different items that get handled differently depending on that type.
        # So, if we pass in an exception, then the mocking library know that it should raise that exception.

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default']) # assert_called_with -> call more than once time
    # Write this tests because we want CHECK THE DATABASE -> WAIT A FEW SECOND -> CHECK AGAIN IF NOT READY