package kr.ai.lineosft.projectmanagement.web.controller;

import kr.ai.lineosft.projectmanagement.domain.project.entity.ProjectStatus;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementStatus;
import kr.ai.lineosft.projectmanagement.domain.project.entity.TaskStatus;
import kr.ai.lineosft.projectmanagement.domain.project.repository.ProjectRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.RequirementRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

@Controller
@RequiredArgsConstructor
public class ViewController {

    private final ProjectRepository projectRepository;
    private final TaskRepository taskRepository;
    private final RequirementRepository requirementRepository;

    @GetMapping("/signup")
    public String signup() {
        return "signup";
    }

    @GetMapping("/login")
    public String login() {
        return "login";
    }

    @GetMapping("/find-account")
    public String findAccount() {
        return "find-account";
    }

    @GetMapping("/profile")
    public String profile() {
        return "profile";
    }

    @GetMapping("/")
    public String index(Model model) {
        long activeProjectCount = projectRepository.countByStatus(ProjectStatus.ACTIVE);
        long completedTaskCount = taskRepository.countByStatus(TaskStatus.DONE);
        long pendingAndReviewCount = requirementRepository.countByStatusIn(
                List.of(RequirementStatus.DEFERRED, RequirementStatus.REVIEWING)
        );

        model.addAttribute("activeProjectCount", activeProjectCount);
        model.addAttribute("completedTaskCount", completedTaskCount);
        model.addAttribute("pendingAndReviewCount", pendingAndReviewCount);

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
