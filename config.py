overwrite_existing = False
save_path = r""
save_full_text = True

# Authentication details
uid = ""
hsh = ""
poster_id = ""

# AVAILABLE FIELDS
#  name (Uploader ID)
#  post_date
#  post_id
#  desc

file_name_format = '{post_date} - {post_id} - {desc}'

# PROBABLY DON'T NEED TO CHANGE THIS
api_url = 'https://justfor.fans/ajax/getPosts.php?UserID={userid}&PosterID={poster_id}&Type=One&StartAt={seq}&Page=Profile&UserHash4={hash}'



# for debugging purposes
if __name__ == "__main__":
    print(api_url.format(userid=uid, hash=hsh, seq=0))