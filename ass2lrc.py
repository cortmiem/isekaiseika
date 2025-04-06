import os
import re
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class LyricElement:
    """Represents an element in the lyrics with its timing and type information."""
    text: str
    time: str  # Time in LRC format (mm:ss:cc)
    element_type: int  # 1 for regular kana, 2 for beginning of kanji reading, 10 for line ending


def parse_ass_line(line: str) -> Tuple[str, str, str]:
    """Parse an ASS line to extract start time, end time, and karaoke text.

    Args:
        line: A line from an ASS file.

    Returns:
        Tuple of (start_time, end_time, karaoke_text)
    """
    # Regular expression to match ASS dialogue line format
    pattern = r'^(?:Comment|Dialogue): \d+,(\d+:\d+:\d+\.\d+),(\d+:\d+:\d+\.\d+),[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,karaoke,(.*?)$'
    match = re.match(pattern, line)

    if match:
        start_time, end_time, karaoke_text = match.groups()
        return start_time, end_time, karaoke_text
    return None, None, None


def convert_ass_time_to_lrc(ass_time: str) -> str:
    """Convert ASS time format (h:mm:ss.cc) to LRC format (mm:ss:cc).

    Args:
        ass_time: Time in ASS format.

    Returns:
        Time in LRC format.
    """
    parts = ass_time.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        seconds_parts = seconds.split('.')
        if len(seconds_parts) == 2:
            seconds, centiseconds = seconds_parts
            # Convert everything to the required format
            minutes_total = int(hours) * 60 + int(minutes)
            return f"{minutes_total:02d}:{seconds}:{int(centiseconds):02d}"
    return "00:00:00"  # Default if parsing fails


def add_time_duration(time_str: str, duration_10ms: int) -> str:
    """Add a duration in 10ms units to a time string in LRC format.

    Args:
        time_str: Time in LRC format (mm:ss:cc).
        duration_10ms: Duration in 10ms units.

    Returns:
        Updated time in LRC format.
    """
    minutes, seconds, centiseconds = time_str.split(':')

    # Convert everything to centiseconds
    total_centiseconds = (int(minutes) * 60 * 100) + (int(seconds) * 100) + int(centiseconds)

    # Add the duration
    total_centiseconds += duration_10ms

    # Convert back to mm:ss:cc format
    new_minutes = total_centiseconds // (60 * 100)
    total_centiseconds %= (60 * 100)
    new_seconds = total_centiseconds // 100
    new_centiseconds = total_centiseconds % 100

    return f"{new_minutes:02d}:{new_seconds:02d}:{new_centiseconds:02d}"


def parse_karaoke_elements(karaoke_text: str) -> List[dict]:
    """Parse karaoke text containing k timing tags and special syntax.

    Args:
        karaoke_text: The karaoke text from an ASS line.

    Returns:
        List of elements with their properties.
    """
    elements = []

    # Remove style tags like {\-A}
    karaoke_text = re.sub(r'{\\-[^}]*}', '', karaoke_text)

    # Split by k tags
    k_tag_pattern = r'{\\k(\d+)}([^{]*)'
    matches = re.findall(k_tag_pattern, karaoke_text)

    current_element = None

    for k_value, text in matches:
        k_value = int(k_value)

        # Check if it's a kanji|<kana pattern
        kanji_match = re.match(r'([^|]+)\|<([^#]+)', text)
        if text.startswith('#|<'):
            # This is a continuation of kana for the previous kanji
            kana = text[3:]  # Remove the #|< prefix
            if current_element and current_element.get('type') == 'kanji_group':
                current_element['kana'].append({
                    'text': kana,
                    'k_value': k_value
                })
        elif kanji_match:
            # This is a kanji with furigana
            kanji, kana = kanji_match.groups()

            if current_element and current_element.get('type') == 'kanji_group':
                # Add kana to the current kanji group
                current_element = {
                    'type': 'kanji_group',
                    'kanji': kanji,
                    'kana': [{
                        'text': kana,
                        'k_value': k_value
                    }]
                }
                elements.append(current_element)
            else:
                # Start a new kanji group
                current_element = {
                    'type': 'kanji_group',
                    'kanji': kanji,
                    'kana': [{
                        'text': kana,
                        'k_value': k_value
                    }]
                }
                elements.append(current_element)
        else:
            # Regular text element
            # Clean up the text
            if text:
                elements.append({
                    'type': 'regular',
                    'text': text,
                    'k_value': k_value
                })
                current_element = None

    return elements


def generate_lrc_from_elements(elements: List[dict], start_time: str) -> Tuple[List[LyricElement], str]:
    """Generate LRC format elements from parsed karaoke elements.

    Args:
        elements: List of parsed karaoke elements.
        start_time: Start time in LRC format.

    Returns:
        Tuple of (lrc_elements, end_time)
    """
    lrc_elements = []
    current_time = start_time

    for element in elements:
        if element['type'] == 'kanji_group':
            # Handle kanji with kana readings
            kanji = element['kanji']
            kana_readings = element['kana']

            kana_elements = []
            for i, kana in enumerate(kana_readings):
                kana_text = kana['text']
                k_value = kana['k_value']

                # For the first kana in a kanji group, use element_type 2
                element_type = 2 if i == 0 else 0

                kana_elements.append(LyricElement(
                    text=kana_text,
                    time=current_time,
                    element_type=element_type
                ))

                # Update the time for the next element
                current_time = add_time_duration(current_time, k_value)

            # Create the kanji group
            kanji_group = {
                'kanji': kanji,
                'kana_elements': kana_elements
            }

            lrc_elements.append(kanji_group)
        else:
            # Handle regular text elements
            text = element['text']
            k_value = element['k_value']

            # Split the text if it contains multiple characters
            for char in text:
                if char == ' ':
                    # Keep space as is
                    lrc_elements.append(LyricElement(
                        text=' ',
                        time=current_time,
                        element_type=1
                    ))
                else:
                    lrc_elements.append(LyricElement(
                        text=char,
                        time=current_time,
                        element_type=1
                    ))

                # Update the time for the next element
                current_time = add_time_duration(current_time, k_value // len(text) if len(text) > 0 else k_value)

    return lrc_elements, current_time


def format_lrc_output(lrc_elements: List, end_time: str) -> str:
    """Format the final LRC output string.

    Args:
        lrc_elements: List of LRC elements.
        end_time: End time in LRC format.

    Returns:
        Formatted LRC string.
    """
    output = []
    i = 0

    while i < len(lrc_elements):
        element = lrc_elements[i]

        if isinstance(element, dict) and 'kanji' in element:
            # This is a kanji group
            kanji = element['kanji']
            kana_elements = element['kana_elements']

            kana_parts = []
            for kana in kana_elements:
                if kana.element_type == 2:
                    # First kana in the group needs the count and time
                    kana_count = len(kana_elements)
                    kana_parts.append(f"[{kana_count}|{kana.time}]{kana.text}")
                else:
                    # Other kanas just need the time
                    kana_parts.append(f"[{kana.time}]{kana.text}")

            output.append(f"{{{kanji}|{''.join(kana_parts)}}}")
        else:
            # Regular element
            output.append(f"[{element.element_type}|{element.time}]{element.text}")

        i += 1

    # Add the end time marker
    output.append(f"[10|{end_time}]")

    return ''.join(output)


def convert_ass_to_lrc(ass_content: str) -> List[str]:
    """Convert ASS content to LRC format.

    Args:
        ass_content: The content of an ASS file.

    Returns:
        List of LRC lines.
    """
    lrc_lines = []

    for line in ass_content.strip().split('\n'):
        start_time, end_time, karaoke_text = parse_ass_line(line)

        if not start_time or not karaoke_text:
            continue

        # Convert the start time to LRC format
        lrc_start_time = convert_ass_time_to_lrc(start_time)

        # Parse the karaoke elements
        karaoke_elements = parse_karaoke_elements(karaoke_text)

        # Generate LRC elements and get the calculated end time
        lrc_elements, calculated_end_time = generate_lrc_from_elements(karaoke_elements, lrc_start_time)

        # Format the final LRC output
        lrc_line = format_lrc_output(lrc_elements, calculated_end_time)
        lrc_lines.append(lrc_line)

    return lrc_lines


def main():
    """Main function to process file input and output."""
    if len(sys.argv) < 2:
        sys.exit(1)

    ass_filename = sys.argv[1]

    if not ass_filename.lower().endswith('.ass'):
        sys.exit(1)

    if not os.path.exists(ass_filename):
        sys.exit(1)

    with open(ass_filename, 'r', encoding='utf-8') as f:
        text = f.read()

    lrc_lines = convert_ass_to_lrc(text)
    lrc_filename = os.path.splitext(ass_filename)[0] + '.lrc'

    with open(lrc_filename, 'w', encoding='utf-8') as f:
        for item in lrc_lines:
            f.write(item + '\n')

if __name__ == "__main__":
    main()
