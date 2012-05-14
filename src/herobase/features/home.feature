Feature: View the home page.
  Scenario: Open home page as unauthenticated user.
    When I access the url "/"
    Then I see the text "Join now!"

  Scenario: Open home page as authenticated user.
    When I access the url "/"
    And I am the user "Horst"
    Then I see the text "Horst"