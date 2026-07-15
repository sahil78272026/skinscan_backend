from typing import List, Optional
from pydantic import BaseModel
import urllib.parse

class Product(BaseModel):
    name: str
    brand: str
    category: str
    description: str
    url: Optional[str] = None
    image_url: Optional[str] = None

PRODUCT_DB = {
    "blemishes": [
        Product(name="Purifying Neem Face Wash", brand="Himalaya", category="Cleanser", description="Formulated for clear skin, helps manage occasional breakouts."),
        Product(name="Bio Winter Green Spot Correcting Cream", brand="Biotique", category="Treatment", description="Targeted application for flawless skin."),
        Product(name="Neem & Turmeric Soap", brand="Himalaya", category="Cleanser", description="Traditional purifying blend for clear pores."),
        Product(name="Tea Tree Skin Clearing Facial Wash", brand="The Body Shop", category="Cleanser", description="Deeply purifies and reduces blemish appearance."),
        Product(name="Bio Myristica Spot Correcting Anti-Blemish Face Pack", brand="Biotique", category="Mask", description="Helps control bacteria that causes breakouts."),
        Product(name="Clarifying Neem & Turmeric Face Wash", brand="Kama Ayurveda", category="Cleanser", description="Gentle yet effective for congested skin."),
        Product(name="Anti-Blemish Cream", brand="Himalaya", category="Treatment", description="Soothes the appearance of marks and spots."),
        Product(name="Bio Clove Purifying Anti-Blemish Face Pack", brand="Biotique", category="Mask", description="Draws out impurities from clogged pores."),
        Product(name="Nimrah Anti Acne Face Pack", brand="Kama Ayurveda", category="Mask", description="Reduces the appearance of blemishes and redness."),
        Product(name="Teatree & Neem Anti Blemish Face Wash", brand="Lotus Herbals", category="Cleanser", description="Balancing wash for oily and congested skin."),
        Product(name="Kashmiri Saffron & Neem Cleanser", brand="Forest Essentials", category="Cleanser", description="Purifying daily wash for clear skin."),
        Product(name="Neem Face Pack", brand="Himalaya", category="Mask", description="Weekly deep cleanse for blemish-prone skin.")
    ],
    "under_eye": [
        Product(name="Under Eye Cream", brand="Himalaya", category="Eye Care", description="Refreshes and brightens the appearance of under-eye shadows."),
        Product(name="Bio Seaweed Revitalizing Eye Gel", brand="Biotique", category="Eye Care", description="Cooling gel to reduce signs of tired eyes."),
        Product(name="Kumkumadi Rejuvenating & Brightening Eye Cream", brand="Kama Ayurveda", category="Eye Care", description="Luxurious cream for reducing dark shadows."),
        Product(name="Intensive Eye Cream with Anise", brand="Forest Essentials", category="Eye Care", description="Deeply hydrating to smooth the under-eye area."),
        Product(name="Almond Under Eye Cream", brand="Biotique", category="Eye Care", description="Nourishing cream to reduce puffiness."),
        Product(name="Nutraeye Rejuvenating Under Eye Gel", brand="Lotus Herbals", category="Eye Care", description="Cooling hydration for tired eyes."),
        Product(name="Youth Eternity Under Eye Cream", brand="Himalaya", category="Eye Care", description="Supports elasticity and brightness."),
        Product(name="Coffee Under Eye Cream", brand="mCaffeine", category="Eye Care", description="Energizes and reduces the appearance of dark circles."),
        Product(name="Bio Almond Eye Cream", brand="Biotique", category="Eye Care", description="Soothes and brightens the delicate eye contour."),
        Product(name="Rose & Papaya Eye Gel", brand="Kama Ayurveda", category="Eye Care", description="Lightweight gel to depuff and refresh.")
    ],
    "dryness": [
        Product(name="Nourishing Skin Cream", brand="Himalaya", category="Moisturizer", description="Deeply hydrates and restores moisture balance."),
        Product(name="Deeply Nourishing Facial Cleanser", brand="Forest Essentials", category="Cleanser", description="Gentle wash that doesn't strip natural oils."),
        Product(name="Bio Morning Nectar Flawless Skin Lotion", brand="Biotique", category="Moisturizer", description="Sinks in quickly for sustained hydration."),
        Product(name="Cocoa Butter Intensive Body Lotion", brand="Himalaya", category="Moisturizer", description="Intensive care for extremely dry patches."),
        Product(name="Eladi Hydrating Ayurvedic Face Cream", brand="Kama Ayurveda", category="Moisturizer", description="Rich and restorative for dry skin types."),
        Product(name="Sandalwood & Orange Peel Cleanser", brand="Forest Essentials", category="Cleanser", description="Hydrating cleanse for a supple finish."),
        Product(name="Bio Saffron Youth Dew Moisturizer", brand="Biotique", category="Moisturizer", description="Rich nourishment for parched skin."),
        Product(name="Aloe Vera Face Wash", brand="Himalaya", category="Cleanser", description="Cooling and hydrating daily wash."),
        Product(name="Shea Butter Moisturizer", brand="Lotus Herbals", category="Moisturizer", description="Locks in moisture for 24 hours."),
        Product(name="Advanced Facial Oil", brand="Kama Ayurveda", category="Oil", description="Seals in hydration and adds a radiant glow.")
    ],
    "uneven_tone": [
        Product(name="Clear Complexion Day Cream", brand="Himalaya", category="Moisturizer", description="Promotes a brighter, more radiant complexion."),
        Product(name="Bio Dandelion Visibly Ageless Serum", brand="Biotique", category="Serum", description="Helps fade the appearance of dark spots."),
        Product(name="Kumkumadi Miraculous Beauty Fluid", brand="Kama Ayurveda", category="Oil", description="Legendary Ayurvedic blend for an even tone."),
        Product(name="Soundarya Radiance Cream", brand="Forest Essentials", category="Moisturizer", description="Infused with 24K gold for luminous skin."),
        Product(name="WhiteGlow Skin Whitening Gel Creme", brand="Lotus Herbals", category="Moisturizer", description="Brightens and evens out skin appearance."),
        Product(name="Bio Fruit Whitening Lip Balm", brand="Biotique", category="Lip Care", description="Evens out tone on delicate lip skin."),
        Product(name="Natural Glow Kesar Face Cream", brand="Himalaya", category="Moisturizer", description="Saffron-infused for a healthy glow."),
        Product(name="Turmeric & Myrrh Skin Brightening Soap", brand="Kama Ayurveda", category="Cleanser", description="Daily wash to reduce uneven pigmentation."),
        Product(name="Tejasvi Brightening Emulsion", brand="Forest Essentials", category="Moisturizer", description="Deeply clarifying and brightening."),
        Product(name="Bio Coconut Whitening & Brightening Cream", brand="Biotique", category="Moisturizer", description="Fades the look of dark spots and patches.")
    ],
    "redness": [
        Product(name="Soothing Aloe Vera Gel", brand="Himalaya", category="Treatment", description="Cools and calms the appearance of irritated skin."),
        Product(name="Pure Rose Water", brand="Forest Essentials", category="Toner", description="Instantly refreshes and soothes redness."),
        Product(name="Bio Aloe Vera Face & Body Sun Lotion", brand="Biotique", category="Sunscreen", description="Protects sensitive skin from environmental stressors."),
        Product(name="Pure Rosewater", brand="Kama Ayurveda", category="Toner", description="Distilled rose water to calm sensitive skin."),
        Product(name="Sensitive Skin Day Cream", brand="Himalaya", category="Moisturizer", description="Gentle formulation for easily irritated skin."),
        Product(name="Aloe & Cucumber Gel", brand="Lotus Herbals", category="Treatment", description="Cooling relief for flushed or sun-exposed skin."),
        Product(name="Bio Cucumber Pore Tightening Toner", brand="Biotique", category="Toner", description="Cooling effect that minimizes the look of redness."),
        Product(name="Sandalwood Soothing Lotion", brand="Kama Ayurveda", category="Moisturizer", description="Traditional calming ingredient for flushed skin."),
        Product(name="Delicate Skin Cleansing Milk", brand="Forest Essentials", category="Cleanser", description="Extremely gentle wash for sensitive barriers."),
        Product(name="Neem & Turmeric Face Wash", brand="Himalaya", category="Cleanser", description="Gentle purifying wash that doesn't strip skin.")
    ],
    "fine_lines": [
        Product(name="Youth Eternity Day Cream", brand="Himalaya", category="Moisturizer", description="Supports skin elasticity and a youthful glow."),
        Product(name="Bio Saffron Youth Dew", brand="Biotique", category="Moisturizer", description="Ayurvedic blend for mature skin nourishment."),
        Product(name="Sanjeevani Beauty Elixir", brand="Forest Essentials", category="Treatment", description="Restores the look of youthful plumpness."),
        Product(name="Anti-Wrinkle Cream", brand="Himalaya", category="Moisturizer", description="Helps smooth the appearance of fine lines."),
        Product(name="Rejuvenating & Brightening Ayurvedic Night Cream", brand="Kama Ayurveda", category="Moisturizer", description="Overnight repair for mature skin."),
        Product(name="YouthRx Anti-Aging Cream", brand="Lotus Herbals", category="Moisturizer", description="Firming and lifting appearance."),
        Product(name="Bio Bxl Cellular Youth Serum", brand="Biotique", category="Serum", description="Concentrated support for loss of firmness."),
        Product(name="Advanced Anti-Aging Cream", brand="Himalaya", category="Moisturizer", description="Targets visible signs of aging."),
        Product(name="Ojas Age Arresting Ayurvedic Sheet Mask", brand="Forest Essentials", category="Mask", description="Instant plumping and hydration boost."),
        Product(name="Amaranth & Saffron Firming Cream", brand="Kama Ayurveda", category="Moisturizer", description="Improves the look of skin elasticity.")
    ]
}

def get_recommendations_for_concerns(concerns: List[str]) -> List[dict]:
    """
    Map AI detected top concerns to cosmetic product categories and return 
    a curated list of up to 5 relevant products.
    """
    concern_mapping = {
        "blemishes": ["blemishes", "clogged pores", "congested", "breakouts", "texture"],
        "under_eye": ["dark circles", "under-eye", "tired eyes", "puffiness"],
        "dryness": ["dry", "dehydrated", "flaking", "dull"],
        "uneven_tone": ["uneven tone", "dark spots", "pigmentation", "radiance"],
        "redness": ["redness", "sensitivity", "irritation", "flushed"],
        "fine_lines": ["fine lines", "wrinkles", "mature", "firmness", "elasticity"]
    }
    
    selected_categories = set()
    for concern in concerns:
        c_lower = concern.lower()
        for cat_key, keywords in concern_mapping.items():
            if any(k in c_lower for k in keywords):
                selected_categories.add(cat_key)
                
    # If no specific categories matched, default to general hydration/glow
    if not selected_categories:
        selected_categories = {"dryness", "uneven_tone"}
        
    recommended_products = []
    # Map generic high-quality skincare images for each category
    category_images = {
        "Cleanser": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?q=80&w=400&auto=format&fit=crop",
        "Moisturizer": "https://images.unsplash.com/photo-1611077544946-82eb11029c92?q=80&w=400&auto=format&fit=crop",
        "Serum": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?q=80&w=400&auto=format&fit=crop",
        "Eye Care": "https://images.unsplash.com/photo-1599305090598-fe179d501227?q=80&w=400&auto=format&fit=crop",
        "Mask": "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?q=80&w=400&auto=format&fit=crop",
        "Treatment": "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?q=80&w=400&auto=format&fit=crop",
        "Toner": "https://images.unsplash.com/photo-1617897903246-719242758050?q=80&w=400&auto=format&fit=crop",
        "Oil": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?q=80&w=400&auto=format&fit=crop",
        "Sunscreen": "https://images.unsplash.com/photo-1556228720-1c27bef96a5b?q=80&w=400&auto=format&fit=crop",
        "Lip Care": "https://images.unsplash.com/photo-1585232004423-244e0e6904e3?q=80&w=400&auto=format&fit=crop"
    }

    # Take 2-3 products from each matched category to form a well-rounded routine
    for cat in selected_categories:
        products = PRODUCT_DB.get(cat, [])
        # Take up to 3 products per category
        for p in products[:3]:
            p_dict = p.model_dump()
            
            # If no hardcoded URL exists, generate a live Google Shopping link
            if not p_dict.get("url"):
                query = urllib.parse.quote(f"{p.brand} {p.name}")
                # We use tbm=shop to link directly to the Google Shopping tab where they can buy it instantly
                p_dict["url"] = f"https://www.google.com/search?tbm=shop&q={query}"
                
            # If no hardcoded image exists, inject a beautiful generic category image
            if not p_dict.get("image_url"):
                fallback_image = "https://images.unsplash.com/photo-1615397323165-27a3a60a74d2?q=80&w=400&auto=format&fit=crop"
                p_dict["image_url"] = category_images.get(p_dict["category"], fallback_image)
                
            recommended_products.append(p_dict)
            
    # Limit to top 6 products overall to avoid overwhelming the user
    return recommended_products[:6]
