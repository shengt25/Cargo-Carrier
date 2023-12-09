import textwrap


def get_story():
    word_list = []
    story_list = [
        "In a world of European cargo aviation, you command your own plane. With 30 European airports at your disposal,"
        "you are tasked with delivering cargo from one airport to another. Your mission is clear: efficiently transport goods,"
        "manage your finances, and reach key objective— accumulate 20 000 EURO. Time is your greatest constraint; you have just 5 game days to achieve these goals.",
        "You can get a great tip by company for a good job, but you also risk becoming a victim of competitors who will damage your cargo,"
        "the fine is almost all your money. If you don’t want to take the risk to unload, just pay 200 EURO to hand over to professional unloader.",
        "Remember - airlines really value flying to different airports, this can work to your advantage ;-)",
        "As you take off on your maiden flight, your journey begins. Your choices and strategy will determine your success or failure."
        "The European skies are yours to navigate, but the path to victory demands cold calculation and skillful decision-making."
        ]

    story_list_long = [
        "In a world where adventure awaited just beyond the horizon, you found yourself at the helm of your very own cargo plane. "
        "The skies of Europe stretched out before you, a canvas of endless possibilities. With a sense of excitement, "
        "you set out on a journey that would challenge your skills and test your resolve. "
        "You stood on the tarmac of your home airport, ready to embark on a quest that few had dared to undertake.",
        "Thirty different European airports beckoned, each holding the promise of unique treasure, fortune, and unforeseen challenges."
        "Your mission was clear: do delivery from one airport to another, earning your keep with each successful flight. "
        "With the plane's engines roaring to life, you took off, soaring over picturesque landscapes and bustling cities. "
        "Your cargo hold was filled with goods from your starting airport, and your journey had begun. But the skies were not always friendly. "
        "Fuel was a precious resource, and you had to make calculated decisions about when and where to refuel. "
        "Emission penalty loomed on the horizon, a reminder of your responsibility to the environment. ",
        "After each flight you had chance to decide how to handle the cargo, to receive an award for a good flight, "
        "but also you could have been a victim of losing all your money. "
        "Remember – companies can reward generously if you fly to different airports and don’t repeat yourself. "
        "Perhaps the greatest challenge of all was the temptation to cancel a delivery when the going got tough. "
        "But handing over came at a cost a hefty 300 EURO that could set you back considerably. ",
        "You knew that your goal was amass a fortune of 20 000 EURO and open your tiny but lovely personal airport – "
        "you have dreamed about this all your life. Time was not your ally in this quest; "
        "you had only about a one month (equivalent to 10 minutes in the real world) to achieve these ambitious objectives.",
        "As you continued your journey, the thrill of the unknown and the promise of riches pushed you forward. "
        "With each take off, you faced challenges, made decisions, and worked toward your goals, "
        "knowing that only the most skilled and determined pilots would succeed. "
        "The skies of Europe held both the allure of adventure and the weight of responsibility. ",
        "Your fate was in your hands, and the journey had only just begun. "
        "Would you rise to the occasion and conquer the challenges of the cargo skies, or would you fall short of your dreams? "
        "The adventure awaited, and it was time to take flight."]

    # set column width to some characters
    wrapper = textwrap.TextWrapper(width=100, break_long_words=False, replace_whitespace=False)
    # wrap text
    for story in story_list:
        word_list.extend("\n")
        word_list.extend(wrapper.wrap(text=story))
    return word_list


if __name__ == "__main__":
    get_story()
