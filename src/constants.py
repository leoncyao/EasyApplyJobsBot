class Constants:
    # Website URLs
    websiteUrl = "www.automated-bots.com"
    contactUrl = "https://www.automated-bots.com/contact"
    linkJobUrl = "https://www.linkedin.com/jobs/search/"
    angelCoUrl = "https://angel.co/login"
    globalLogicUrl = "https://www.globallogic.com/career-search-page/"

    # Job Search Settings
    jobsPerPage = 25
    max_urls = 600  # Maximum number of job URLs to inspect
    max_successful_applications = 200  # Maximum number of successful applications per run

    # Bot Speed Settings
    fast = 2
    medium = 3
    slow = 5
    botSpeed = 0.5  # Current bot speed setting

    # LinkedIn Job Page Elements
    jobsPageUrl = "https://www.linkedin.com/jobs"
    jobsPageCareerClass = "//div[contains(@class, 'careers')]"
    testJobUrl = "https://www.linkedin.com/jobs/search/?currentJobId=3577461385&distance=25&f_AL=true&f_E=2&f_JT=F%2CP%2CC&f_SB2=3&f_WT=1%2C2%2C3&geoId=102221843&keywords=frontend"
    totalJobs = "//small"
    testPageUrl = testJobUrl + "&start=" + str(2)
    offersPerPage = "//li[@data-occludable-job-id]"
    easyApplyButton = '//button[contains(@class, "jobs-apply-button")]'

    # Application Process Settings
    max_application_attempts = 10  # Maximum number of attempts for each application step
    application_delay = 1  # Delay between application steps in seconds
    retry_delay = 60  # Delay between retrying failed applications in seconds

    # Form Handling Settings
    default_text_input = "5"  # Default value for text inputs
    default_textarea = "I am a software engineer with a passion for building scalable and efficient systems."
    default_select_index = 1  # Default index for select/dropdown fields

    # Data File Paths
    job_data_file = "data/job_data.json"
    failed_applications_file = "data/failed_applications.json"
    application_results_file = "data/application_results.json"
    questions_file = "data/questions.json"
    url_data_file = "data/urlData.txt"

# Create a singleton instance
constants = Constants()
