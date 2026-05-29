package kr.ai.lineosft.projectmanagement.web.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ViewController {

    @GetMapping("/signup")
    public String signup() {
        return "signup";
    }

    @GetMapping("/login")
    public String login() {
        return "login";
    }

    @GetMapping("/")
    public String index() {
        return "index";
    }

    @GetMapping("/projects")
    public String projects() {
        return "projects";
    }

    @GetMapping("/projects/{id}")
    public String projectDetail() {
        return "project-detail";
    }

    @GetMapping("/schedule")
    public String schedule() {
        return "schedule";
    }
}
