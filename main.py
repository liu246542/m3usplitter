import re
from collections import defaultdict
from pathlib import Path

class M3UParser:
    def __init__(self, input_file):
        self.input_file = input_file
        self.header = []
        self.channels = defaultdict(list)
    def update_group_title(self, channel_info, new_group):
        """Update the group-title in channel info with new group name"""
        # Replace existing group-title if it exists
        if 'group-title="' in channel_info:
            updated_info = re.sub(r'group-title="[^"]*"', f'group-title="{new_group}"', channel_info)
        else:
            # Add group-title if it doesn't exist (insert before the first double quote after #EXTINF)
            position = channel_info.find('"')
            if position != -1:
                updated_info = channel_info[:position] + f'group-title="{new_group}" ' + channel_info[position:]
            else:
                updated_info = channel_info  # Keep original if no quotes found
        return updated_info
    def parse_file(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Store header (first line if it's #EXTM3U)
        if lines[0].startswith('#EXTM3U'):
            self.header = [lines[0]]
            lines = lines[1:]
        # Process channels
        i = 0
        while i < len(lines):
            if lines[i].startswith('#EXTINF'):
                if i + 1 < len(lines):
                    channel_info = lines[i]
                    channel_url = lines[i + 1]
                    # Extract source from URL
                    url_sources = ['gaoma', 'bestzb', 'ystenlive', 'wasusyt', 'gitv']
                    source_found = False
                    for source in url_sources:
                        if source in channel_url:
                            # Update group-title before adding to channels
                            updated_info = self.update_group_title(channel_info, source)
                            self.channels[source].extend([updated_info, channel_url])
                            source_found = True
                            break
                    # If no source matched, add to foobar group
                    if not source_found:
                        updated_info = self.update_group_title(channel_info, "foobar")
                        self.channels["foobar"].extend([updated_info, channel_url])
                i += 2
            else:
                i += 1

    def write_group_files(self, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for source, content in self.channels.items():
            if content:  # Only create file if there are channels in the source
                output_file = output_dir / f'{source}.m3u'
                with open(output_file, 'w', encoding='utf-8') as f:
                    # Write header
                    f.writelines(self.header)
                    # Write channels
                    f.writelines(content)

def main():
    # Create parser instance
    parser = M3UParser('tv.m3u')
    # Parse the file
    parser.parse_file()
    # Write separated files
    parser.write_group_files('output')
if __name__ == '__main__':
    main()
