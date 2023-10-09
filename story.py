import textwrap


def get_story():
    story = """"In a world where adventure awaited just beyond the horizon, you found yourself at the helm of your very own cargo plane. 
    The skies of Europe stretched out before you, a canvas of endless possibilities. 
    With a sense of excitement, you set out on a journey that would challenge your skills and test your resolve. 

    You stood on the tarmac of your home airport, ready to embark on a quest that few had dared to undertake. 
    Thirty different European airports beckoned, each holding the promise of unique cargo, fortune, and unforeseen challenges. 
    Your mission was clear: deliver cargo from one airport to another, earning your keep with each successful flight. 
    With the plane's engines roaring to life, you took off, soaring over picturesque landscapes and bustling cities. 
    Your cargo hold was filled with goods from your starting airport, and your journey had begun. But the skies were not always friendly. 
    Fuel was a precious resource, and you had to make calculated decisions about when and where to refuel. 
    Emission payments loomed on the horizon, a reminder of your responsibility to the environment. 
    After each flight you had chance to receive an award for a good flight, but also you could have been a victim of robbery and lose all your money. 
    Remember – companies can reward generously if you fly to different airports and don’t repeat yourself. 
    Perhaps the greatest challenge of all was the temptation to cancel a delivery when the going got tough. 
    But cancelling came at a cost—a hefty 200 EURO fine that could set you back considerably. You knew that your goal was amass a fortune of 10 000 EURO and open your personal airport – you have dreamed about this all your life. 
    Time was not your ally in this quest; you had only about a one month (equivalent to 10 minutes in the real world) to achieve these ambitious objectives.

    As you continued your journey, the thrill of the unknown and the promise of riches pushed you forward. With each take off, you faced challenges, made decisions, and worked toward your goals, knowing that only the most skilled and determined pilots would succeed. The skies of Europe held both the allure of adventure and the weight of responsibility. Your fate was in your hands, and the journey had only just begun. Would you rise to the occasion and conquer the challenges of the cargo skies, or would you fall short of your dreams? The adventure awaited, and it was time to take flight.
"""

    # set column width to 90 characters
    wrapper = textwrap.TextWrapper(width=90, break_long_words=False, replace_whitespace=False)
    # wrap text
    word_list = wrapper.wrap(text=story)
    return word_list


if __name__ == "__main__":
    get_story()
