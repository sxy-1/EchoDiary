import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_table(ax, title, columns, x, y, cell_height=0.5, cell_width=2):
    ax.text(x + cell_width/2, y + cell_height, title, ha='center', va='center', weight='bold', fontsize=12)
    for i, column in enumerate(columns):
        rect = patches.Rectangle((x, y - (i+1)*cell_height), cell_width, cell_height, linewidth=1, edgecolor='black', facecolor='none')
        ax.add_patch(rect)
        ax.text(x + cell_width/2, y - (i+1)*cell_height + cell_height/2, column, ha='center', va='center', fontsize=10)

fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 10)
ax.set_ylim(-15, 2)
ax.axis('off')

# User Database
draw_table(ax, 'CopyUsers', ['user_id (PRIMARY KEY)', 'username', 'email', 'password (encrypted)', 'created_at', 'last_login'], 1, 1)
draw_table(ax, 'Profiles', ['profile_id (PRIMARY KEY)', 'user_id (FOREIGN KEY referencing Users.user_id)', 'name', 'bio', 'location'], 5, 1)
draw_table(ax, 'Preferences', ['pref_id (PRIMARY KEY)', 'user_id (FOREIGN KEY referencing Users.user_id)', 'color_theme', 'font_size', '...'], 9, 1)

# Diary Database
draw_table(ax, 'CopyEntries', ['entry_id (PRIMARY KEY)', 'user_id (FOREIGN KEY referencing Users.user_id)', 'title', 'content', 'created_at', 'updated_at', 'word_count', 'location (optional GPS coordinates)'], 1, -8)
draw_table(ax, 'Tags', ['tag_id (PRIMARY KEY)', 'tag_name'], 5, -8)
draw_table(ax, 'EntryTags', ['id (PRIMARY KEY)', 'entry_id (FOREIGN KEY referencing Entries.entry_id)', 'tag_id (FOREIGN KEY referencing Tags.tag_id)'], 9, -8)

plt.show()
