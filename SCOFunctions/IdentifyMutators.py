from SCOFunctions.SC2Dictionaries import Mutators, mutator_ids

# Create mutator list by removing my mutators and those that are not in custom mutations
mutators_list = list(Mutators.keys())[:-19]
for item in ('Nap Time', 'Stone Zealots', 'Chaos Studios', 'Undying Evil', 'Afraid of the Dark', 'Trick or Treat', 'Turkey Shoot',
             'Sharing Is Caring', 'Gift Exchange', 'Naughty List', 'Extreme Caution', 'Insubordination', 'Fireworks', 'Lucky Envelopes',
             'Sluggishness'):
    mutators_list.remove(item)


def get_mutator(button, panel):
    """ Returns mutator based on button (41-83) and currently selected panel (1-4) """
    button = (button - 41) // 3 + (panel - 1) * 15
    if 0 <= button < len(mutators_list):
        return mutators_list[button]
    else:
        return None


def identify_mutators(events, extension=True, mm=False):
    """ Identify mutators based on dirty STriggerDialogControl events
    This work only in custom mutations, and random mutator isn't decided."""
    mutators = list()

    # MM maps
    if mm:
        for event in events:
            if event['_event'] == 'NNet.Replay.Tracker.SUpgradeEvent' and event['m_playerId'] == 0:
                upgrade_name = event['m_upgradeTypeName'].decode()
                if 'mutatorinfo' in upgrade_name:
                    mutator_id = upgrade_name[12:]
                    if mutator_id in mutator_ids:
                        mutators.append(mutator_ids[mutator_id])

    # Custom mutation
    if extension:
        # Get a list of dialog items used
        actions = list()
        offset = 0
        last_game_loop = None  # Save the last gameloop. Don't count multiple clicks done on the same loop, game will ignore them.

        for event in events:
            if event['_gameloop'] == 0 and event['_event'] == 'NNet.Game.STriggerDialogControlEvent' and event[
                    'm_eventType'] == 3 and 'SelectionChanged' in event['m_eventData']:
                offset = 129 - event['m_controlId']

            elif event['_gameloop'] > 0 and event['_gameloop'] != last_game_loop and event[
                    '_event'] == 'NNet.Game.STriggerDialogControlEvent' and event['_userid']['m_userId'] == 0:
                actions.append(event['m_controlId'] + offset)
                last_game_loop = event['_gameloop']

            # Break on game starting
            elif event['_event'] == 'NNet.Replay.Tracker.SUpgradeEvent' and event['m_playerId'] in [
                    1, 2
            ] and 'Spray' in event['m_upgradeTypeName'].decode():
                break

        panel = 1  # Currently visible mutator panel
        for action in actions:
            # Mutator clicked
            if 41 <= action <= 83:
                new_mutator = get_mutator(action, panel)
                if new_mutator != None and (not new_mutator in mutators or new_mutator == 'Random'):
                    mutators.append(new_mutator)

            # Panel Changed
            if action == 123 and panel > 1:
                panel -= 1
            if action == 124 and panel < 4:
                panel += 1

            # Mutator removed
            if 88 <= action <= 106:
                del mutators[(action - 88) // 2]

    # Fix HftS old
    return tuple(m.replace('Heroes from the Storm (old)', 'Heroes from the Storm').replace('Extreme Caution', 'Afraid of the Dark') for m in mutators)
