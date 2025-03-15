import re
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PySide6.QtGui import QDragEnterEvent, QDropEvent

def ass_to_karaoke_format(ass_text):
    result = []
    lines = ass_text.strip().split('\n')

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Extract the karaoke part
        karaoke_match = re.search(r'karaoke,(.*?)$', line)
        if not karaoke_match:
            continue

        karaoke_content = karaoke_match.group(1)

        # Remove style tags like {\-A}, {\-B}
        karaoke_content = re.sub(r'{\\-[A-Z]}', '', karaoke_content)

        # Extract start time from the line
        time_match = re.search(r'0:(\d+:\d+\.\d+),', line)
        if not time_match:
            continue

        start_time_str = time_match.group(1)
        # Convert to seconds for calculations
        minutes, rest = start_time_str.split(':')
        seconds, milliseconds = rest.split('.')
        start_time_seconds = int(minutes) * 60 + int(seconds) + int(milliseconds) / 100

        # Current position in seconds
        current_time = start_time_seconds

        # Process the content
        output_line = ""

        # Find all karaoke segments and text
        segments = re.findall(r'{\\k(\d+)}(.*?)(?=(?:{\\k)|$)', karaoke_content)

        i = 0
        while i < len(segments):
            k_value, text = segments[i]
            k_seconds = int(k_value) / 100  # Convert k value to seconds

            # Process text segments
            syllable_match = re.search(r'([^|<]+)\|<(.+)', text)
            if syllable_match:
                # This is a complex segment with kanji and furigana
                kanji = syllable_match.group(1)
                furigana = syllable_match.group(2)

                # Count how many furigana characters
                furigana_parts = []
                j = i + 1
                while j < len(segments) and "#|<" in segments[j][1]:
                    furigana += segments[j][1].split("#|<")[1]
                    k_seconds += int(segments[j][0]) / 100
                    j += 1

                # Format timestamps for kanji with furigana
                current_time_formatted = format_time(current_time)

                # Now collect all the furigana parts with their timestamps
                furigana_parts = []
                temp_time = current_time

                # First part
                furigana_parts.append(f"[{current_time_formatted}]{furigana[0]}")
                temp_time += k_seconds / len(furigana)

                # Remaining parts
                for char in furigana[1:]:
                    temp_time_formatted = format_time(temp_time)
                    furigana_parts.append(f"[{temp_time_formatted}]{char}")
                    temp_time += k_seconds / len(furigana)

                # Format the output
                furigana_str = "".join(furigana_parts)
                output_line += f"{{{kanji}|[{len(furigana)}|{current_time_formatted}]{remove_first_bracketed_content(furigana_str)}}}"

                current_time += k_seconds
                i = j
            elif text.strip():
                # This is a simple syllable
                current_time_formatted = format_time(current_time)
                output_line += f"[1|{current_time_formatted}]{text}"
                current_time += k_seconds
                i += 1
            else:
                # This might be a space or other character
                output_line += text
                current_time += k_seconds
                i += 1

        # Add line ending time
        end_time_formatted = format_time(current_time)
        output_line += f"[10|{end_time_formatted}]"

        result.append(output_line)

    return "\n".join(result)


def remove_first_bracketed_content(s):
    return re.sub(r'^\[[^]]*]', '', s, count=1)


def format_time(seconds):
    # Convert seconds to MM:SS:mm format
    minutes = int(seconds // 60)
    seconds_remainder = seconds % 60
    whole_seconds = int(seconds_remainder)
    milliseconds = int((seconds_remainder - whole_seconds) * 100)

    return f"{minutes:02d}:{whole_seconds:02d}:{milliseconds:02d}"


class ASSProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ASS2LRC by Asuharayuuki")
        self.setGeometry(100, 100, 600, 400)

        self.text_edit = QTextEdit(self)
        self.text_edit.setAcceptDrops(False)  # 让窗口接收拖拽

        self.process_button = QPushButton("Ciallo～(∠・ω< )⌒☆", self)
        self.process_button.clicked.connect(self.process_text)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.process_button)
        self.setLayout(layout)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_edit.setPlainText(file.read())
            except Exception as e:
                self.text_edit.setPlainText(f"Error: {str(e)}")

    def process_text(self):
        input_text = self.text_edit.toPlainText()
        output_text = ass_to_karaoke_format(input_text)
        self.text_edit.setPlainText(output_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ASSProcessor()
    window.show()
    sys.exit(app.exec())
