import os
import requests
from google import genai
from google.genai import types

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

    # ২. এআই দিয়ে পোস্টের সাথে মানানসই ছবি জেনারেট করা (Imagen 3 মডেল ব্যবহার করে)
    image_path = "generated_image.png"
    image_generated = False
    
    try:
        print("Generating image with AI...")
        image_prompt = (
            "A clean, modern, minimalist vector illustration representing coding, software engineering, "
            "and technology, vibrant colors, high quality, social media friendly."
        )
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=image_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/png",
                aspect_ratio="1:1",
            )
        )
        for generated_image in result.generated_images:
            image_bytes = generated_image.image.image_bytes
            with open(image_path, "wb") as f:
                f.write(image_bytes)
        image_generated = True
        print("Image generated successfully!")
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
        # ছবি ছাড়া শুধু টেক্সট পোস্ট করার ব্যাকআপ পদ্ধতি
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
