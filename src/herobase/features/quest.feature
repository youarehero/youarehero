Feature: Manage quests
    Scenario: Create a quest
        When I access the url "quest-create"
        And I am logged in as user "horst"
        And I enter "Eine Quest" into the field "title"
        And I enter "Eine Beschreibung" into the field "description"
        And I enter "0" into the field "hero_class"
        And I enter "1" into the field "max_heroes"
        And I enter "Heidelberg" into the field "location"
        And I enter "12/12/12" into the field "due_date"
        And I enter "1" into the field "level"
        And I submit the form
        Then I see the text "Eine Quest"
        And I see the text "deine Quest"