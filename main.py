import os
import urllib.parse
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
    
    # ১. আকর্ষণীয় ক্যাপশন বা পোস্ট টেক্সট জেনারেট করা
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

    # ২. টেক্সটের মূল বিষয়ের সাথে মিলিয়ে ডাইনামিক ইমেজ প্রম্পট ও লিংক তৈরি করা
    # এখানে জেমিনি থেকে পাওয়া লেখার মূল ভাব বা সাধারণ কোডিং থিম ব্যবহার করে এআই ইমেজ লিংক তৈরি হবে
    image_theme_prompt = (
        "A modern minimalist tech vector illustration representing software engineering, "
        "programming tips, clean code, vibrant neon accents, high resolution, social media graphic"
    )
    
    encoded_prompt = urllib.parse.quote(image_theme_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    print(f"Generated Image URL: {image_url}")

    # ৩. ফেসবুক পেজে ছবি ও টেক্সট একসাথে পোস্ট করা
    url = f"https://graph.facebook.com/v18.0/{fb_page_id}/photos"
    payload = {
        'message': post_content,
        'url': image_url, # ফেসবুক সরাসরি এই লিংক থেকে ছবি ফেচ করে নেবে
        'access_token': fb_token
    }

    try:
        print("Sending photo post to Facebook...")
        res = requests.post(url, data=payload)
        result_data = res.json()
        
        if res.status_code == 200:
            print(f"Successfully posted photo to Facebook! Post ID: {result_data.get('id')}")
        else:
            print(f"Failed to post photo to Facebook: {result_data}")
            
            # ব্যাকআপ পদ্ধতি: কোনো কারণে ফটো পোস্ট ফেইল করলে শুধু টেক্সট পোস্ট করে দেবে
            fallback_url = f"https://graph.facebook.com/v18.0/{fb_page_id}/feed"
            fallback_payload = {'message': post_content, 'access_token': fb_token}
            fallback_res = requests.post(fallback_url, data=fallback_payload)
            if fallback_res.status_code == 200:
                print("Fallback successful: Posted as text-only.")
            else:
                print(f"Fallback failed: {fallback_res.json()}")
                
    except Exception as e:
        print(f"HTTP Request failed: {e}")

if __name__ == "__main__":
    main()
