#!/usr/bin/env python3
"""
Comprehensive Selenium test suite for the contact modal functionality.
Tests all aspects including modal behavior, form validation, accessibility, and responsiveness.
"""

import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os

class ContactModalTests(unittest.TestCase):
    """Test suite for contact modal functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_url = "http://localhost:8000/test-modal-comprehensive.html"
        
        # Try different browsers
        cls.drivers = []
        
        # Chrome
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            cls.drivers.append(('Chrome', webdriver.Chrome(options=chrome_options)))
        except Exception as e:
            print(f"Chrome not available: {e}")
        
        # Firefox
        try:
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument('--headless')
            cls.drivers.append(('Firefox', webdriver.Firefox(options=firefox_options)))
        except Exception as e:
            print(f"Firefox not available: {e}")
    
    def setUp(self):
        """Set up for each test"""
        self.current_driver = None
    
    def tearDown(self):
        """Clean up after each test"""
        if self.current_driver:
            self.current_driver.quit()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        for name, driver in cls.drivers:
            try:
                driver.quit()
            except:
                pass
    
    def test_modal_open_close_chrome(self):
        """Test modal opening and closing in Chrome"""
        if not any(name == 'Chrome' for name, _ in self.drivers):
            self.skipTest("Chrome not available")
        
        name, driver = next((n, d) for n, d in self.drivers if n == 'Chrome')
        self.current_driver = driver
        
        driver.get(self.test_url)
        wait = WebDriverWait(driver, 10)
        
        # Test modal opening
        trigger = wait.until(EC.element_to_be_clickable((By.ID, "test-trigger")))
        trigger.click()
        
        modal = wait.until(EC.visibility_of_element_located((By.ID, "contact-modal")))
        self.assertTrue(modal.is_displayed(), "Modal should be visible after clicking trigger")
        
        # Test close button
        close_btn = driver.find_element(By.ID, "modal-close")
        close_btn.click()
        
        wait.until(EC.invisibility_of_element_located((By.ID, "contact-modal")))
        self.assertFalse(modal.is_displayed(), "Modal should be hidden after clicking close")
    
    def test_modal_open_close_firefox(self):
        """Test modal opening and closing in Firefox"""
        if not any(name == 'Firefox' for name, _ in self.drivers):
            self.skipTest("Firefox not available")
        
        name, driver = next((n, d) for n, d in self.drivers if n == 'Firefox')
        self.current_driver = driver
        
        driver.get(self.test_url)
        wait = WebDriverWait(driver, 10)
        
        # Test modal opening
        trigger = wait.until(EC.element_to_be_clickable((By.ID, "test-trigger")))
        trigger.click()
        
        modal = wait.until(EC.visibility_of_element_located((By.ID, "contact-modal")))
        self.assertTrue(modal.is_displayed(), "Modal should be visible after clicking trigger")
        
        # Test Escape key
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        
        wait.until(EC.invisibility_of_element_located((By.ID, "contact-modal")))
        self.assertFalse(modal.is_displayed(), "Modal should be hidden after pressing Escape")
    
    def test_form_validation(self):
        """Test form validation across browsers"""
        for name, driver in self.drivers:
            with self.subTest(browser=name):
                self.current_driver = driver
                driver.get(self.test_url)
                wait = WebDriverWait(driver, 10)
                
                # Open modal
                trigger = wait.until(EC.element_to_be_clickable((By.ID, "test-trigger")))
                trigger.click()
                
                # Test empty form submission
                submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
                submit_btn.click()
                
                # Check if form validation prevents submission
                email_field = driver.find_element(By.ID, "contact-email")
                is_required = email_field.get_attribute("required")
                self.assertEqual(is_required, "true", "Email field should be required")
                
                # Test invalid email
                email_field.send_keys("invalid-email")
                message_field = driver.find_element(By.ID, "contact-message")
                message_field.send_keys("Test message")
                
                # Check email validation
                email_valid = driver.execute_script("return arguments[0].checkValidity()", email_field)
                self.assertFalse(email_valid, "Invalid email should fail validation")
                
                # Test valid form
                email_field.clear()
                email_field.send_keys("test@example.com")
                
                email_valid = driver.execute_script("return arguments[0].checkValidity()", email_field)
                self.assertTrue(email_valid, "Valid email should pass validation")
    
    def test_focus_management(self):
        """Test focus management and keyboard navigation"""
        for name, driver in self.drivers:
            with self.subTest(browser=name):
                self.current_driver = driver
                driver.get(self.test_url)
                wait = WebDriverWait(driver, 10)
                
                # Open modal
                trigger = wait.until(EC.element_to_be_clickable((By.ID, "test-trigger")))
                trigger.click()
                
                # Check focus moves to first input
                email_field = wait.until(EC.element_to_be_focused())
                self.assertEqual(email_field.get_attribute("id"), "contact-email", 
                               "Focus should move to email field when modal opens")
                
                # Test tab navigation
                ActionChains(driver).send_keys(Keys.TAB).perform()
                
                # Check focus moves to next element
                focused_element = driver.switch_to.active_element
                self.assertEqual(focused_element.get_attribute("tagName"), "TEXTAREA", 
                               "Tab should move focus to textarea")
    
    def test_responsive_design(self):
        """Test responsive design across different viewport sizes"""
        viewport_sizes = [
            (1920, 1080, "Desktop"),
            (768, 1024, "Tablet"),
            (375, 667, "Mobile")
        ]
        
        for name, driver in self.drivers:
            for width, height, device_name in viewport_sizes:
                with self.subTest(browser=name, device=device_name):
                    self.current_driver = driver
                    driver.set_window_size(width, height)
                    driver.get(self.test_url)
                    wait = WebDriverWait(driver, 10)
                    
                    # Open modal
                    trigger = wait.until(EC.element_to_be_clickable((By.ID, "test-trigger")))
                    trigger.click()
                    
                    modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal-container")))
                    
                    # Check modal is visible and properly sized
                    modal_size = modal.size
                    viewport_size = driver.get_window_size()
                    
                    self.assertLess(modal_size['width'], viewport_size['width'], 
                                  f"Modal should fit within {device_name} viewport width")
                    self.assertLess(modal_size['height'], viewport_size['height'], 
                                  f"Modal should fit within {device_name} viewport height")
    
    def test_formspree_integration(self):
        """Test Formspree form action URL"""
        for name, driver in self.drivers:
            with self.subTest(browser=name):
                self.current_driver = driver
                driver.get(self.test_url)
                
                form = driver.find_element(By.ID, "contact-form")
                action_url = form.get_attribute("action")
                
                self.assertEqual(action_url, "https://formspree.io/f/xzzvkzkg", 
                               "Form action should point to correct Formspree endpoint")
    
    def test_aria_attributes(self):
        """Test ARIA attributes for accessibility"""
        for name, driver in self.drivers:
            with self.subTest(browser=name):
                self.current_driver = driver
                driver.get(self.test_url)
                
                modal = driver.find_element(By.ID, "contact-modal")
                
                # Check ARIA attributes
                role = modal.get_attribute("role")
                self.assertEqual(role, "dialog", "Modal should have role='dialog'")
                
                aria_hidden = modal.get_attribute("aria-hidden")
                self.assertEqual(aria_hidden, "true", "Modal should initially have aria-hidden='true'")
                
                aria_labelledby = modal.get_attribute("aria-labelledby")
                self.assertEqual(aria_labelledby, "contact-modal-title", 
                               "Modal should reference title via aria-labelledby")
    
    def test_overlay_click(self):
        """Test clicking outside modal to close"""
        for name, driver in self.drivers:
            with self.subTest(browser=name):
                self.current_driver = driver
                driver.get(self.test_url)
                wait = WebDriverWait(driver, 10)
                
                # Open modal
                trigger = wait.until(EC.element_to_be_clickable((By.ID, "test-trigger")))
                trigger.click()
                
                modal = wait.until(EC.visibility_of_element_located((By.ID, "contact-modal")))
                
                # Click on overlay (outside modal content)
                overlay = driver.find_element(By.CLASS_NAME, "modal-overlay")
                ActionChains(driver).move_to_element_with_offset(overlay, 10, 10).click().perform()
                
                wait.until(EC.invisibility_of_element_located((By.ID, "contact-modal")))
                self.assertFalse(modal.is_displayed(), "Modal should close when clicking outside")

def run_tests():
    """Run all tests and generate report"""
    print("Starting comprehensive modal tests...")
    
    # Start local server if not running
    import subprocess
    import os
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(ContactModalTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)