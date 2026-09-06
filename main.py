import os
import requests
from google import genai

def main():
    # গিটহাব সিক্রেট থেকে ভেরিয়েবল লোড করা
    gemini_key = os.environ.get("GEMINI_API_KEY")
    fb_token = os.environ.get("FB_ACCESS_TOKEN")
    fb_page_id = os.environ.get("FB_PAGE_ID")

    if not gemini_key or not fb_token or not fb_page_id:
        print("Error: Missing required environment variables. Check your GitHub Secrets.")
        return

    client = genai.Client(api_key=gemini_key)
    
    # ১. আকর্ষণীয় ক্যাপশন বা পোস্ট টেক্সট জেনারেট করা (আপনার কাঙ্ক্ষিত gemini-3.6-flash মডেল দিয়ে)
    text_prompt = (
        "Write a short, highly engaging social media post for American tech professionals "
        "about a useful programming or technology tip. Include relevant, trending hashtags."
    )
    
    try:
        print("Generating post content with AI...")
        text_response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=text_prompt,
        )
        post_content = text_response.text
        print(f"Generated Content:\n{post_content}\n")
    except Exception as e:
        print(f"Failed to generate content from Gemini: {e}")
        return

    # ২. এআই দিয়ে ছবি জেনারেট করা (লেটেস্ট ডেভেলপার এপিআই নিয়ম অনুযায়ী generate_content ব্যবহার করে)
    image_path = "generated_image.png"
    image_generated = False
    
    try:
        print("Generating image with AI...")
        image_prompt = (
            "A clean, modern, minimalist vector illustration representing coding, software engineering, "
            "and technology, vibrant colors, high quality, social media friendly."
        )
        
        # ডেভেলপার এপিআই নিয়মে image মডেল দিয়ে generate_content কল করা
        image_response = client.models.generate_content(
            model='imagen-3.0-generate-002',
            contents=image_prompt,
        )
        
        # রেসপন্স থেকে ইমেজ বাইট খুঁজে বের করে সেভ করা
        for part in image_response.parts:
            if getattr(part, 'inline_data', None):
                with open(image_path, "wb") as f:
                    f.write(part.inline_data.data)
                image_generated = True
                print("Image generated successfully!")
                break
                
    except Exception as e:
        print(f"Image generation failed, proceeding with text-only post: {e}")

    # ৩. ফেসবুক পেজে পোস্ট পাঠানো (ছবি থাকলে ফটো পোস্ট, না থাকলে সাধারণ টেক্সট পোস্ট)
    if image_generated and os.path.exists(image_path):
        url = f"https://graph.facebook.com/v18.0/{fb_page_id}/photos"
        payload = {
            'message': post_content,
            'access_token': fb_token
        }
        files = {
            'source': open(image_path, 'rb')
        }
        try:
            print("Sending photo post to Facebook...")
            res = requests.post(url, data=payload, files=files)
            result_data = res.json()
            if res.status_code == 200:
                print(f"Successfully posted photo to Facebook! Post ID: {result_data.get('id')}")
            else:
                print(f"Failed to post photo to Facebook: {result_data}")
        except Exception as e:
            print(f"HTTP Request failed: {e}")
    else:
        # ছবি তৈরি না হলে শুধু টেক্সট পোস্ট করার ব্যাকআপ পদ্ধতি
        url = f"https://graph.facebook.com/v18.0/{fb_page_id}/feed"
        payload = {
            'message': post_content,
            'access_token': fb_token
        }
        try:
            print("Sending text post to Facebook...")
            res = requests.post(url, data=payload)
            result_data = res.json()
            if res.status_code == 200:
                print(f"Successfully posted text to Facebook! Post ID: {result_data.get('id')}")
            else:
                print(f"Failed to post text to Facebook: {result_data}")
        except Exception as e:
            print(f"HTTP Request failed: {e}")

if __name__ == "__main__":
    main()
