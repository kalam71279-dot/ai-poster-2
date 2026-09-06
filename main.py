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
    
    # ১. জেমিনি দিয়ে পোস্টের টেক্সট এবং ছবির জন্য ইউনিক প্রম্পট একসাথে জেনারেট করা
    prompt_instruction = (
        "You are a social media manager for tech professionals. "
        "Create two things separated by '|||':\n"
        "1. A short, highly engaging social media post about a useful programming or technology tip with trending hashtags.\n"
        "2. A short, highly specific, and creative visual description (image prompt) for an AI image generator "
        "that visually represents this exact tip (e.g., specific objects, UI elements, or metaphors, avoid generic text).\n\n"
        "Format: [Post Text]|||[Image Prompt]"
    )
    
    try:
        print("Generating post content and unique image prompt with AI...")
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt_instruction,
        )
        
        response_text = response.text
        if "|||" in response_text:
            post_content, image_prompt = response_text.split("|||", 1)
            post_content = post_content.strip()
            image_prompt = image_prompt.strip()
        else:
            # ব্যাকআপ যদি সেপারেশন কাজ না করে
            post_content = response_text
            image_prompt = "Modern abstract technology and programming concept, vibrant colors, minimalist vector art"

        print(f"Generated Content:\n{post_content}\n")
        print(f"Generated Unique Image Prompt: {image_prompt}\n")
        
    except Exception as e:
        print(f"Failed to generate content from Gemini: {e}")
        return

    # ২. জেমিনির তৈরি করা ইউনিক ইমেজ প্রম্পট দিয়ে ডাইনামিক লিংক তৈরি করা
    encoded_prompt = urllib.parse.quote(image_prompt)
    # ছবির ক্যাশ এড়ানোর জন্য শেষে একটি র্যান্ডম সিড বা টাইমস্ট্যাম্প যুক্ত করা যেতে পারে, তবে সাধারণ এনকোড করাই যথেষ্ট
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&nologo=true"
    print(f"Generated Image URL: {image_url}")

    # ৩. ফেসবুক পেজে ছবি ও টেক্সট একসাথে পোস্ট করা
    url = f"https://graph.facebook.com/v18.0/{fb_page_id}/photos"
    payload = {
        'message': post_content,
        'url': image_url,
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
            
            # ব্যাকআপ পদ্ধতি: ফটো পোস্ট ফেইল করলে শুধু টেক্সট পোস্ট করে দেবে
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
