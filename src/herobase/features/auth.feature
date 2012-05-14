Feature: Log in and Log out.
    Scenario: View the Log in page.
        When I access the url "auth_login"
        Then I see the text "username"
        And I see the text "password"

    Scenario: Login to the Page.
        When I access the url "auth_login"
        And the user "horst" with password "password" exists
        And I enter "horst" into the field "username"
        And I enter "password" into the field "password"
        And I submit the form
        Then I am logged in as "horst"