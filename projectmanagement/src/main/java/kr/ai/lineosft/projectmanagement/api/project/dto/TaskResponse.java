package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.Task;
import kr.ai.lineosft.projectmanagement.domain.project.entity.TaskPriority;
import kr.ai.lineosft.projectmanagement.domain.project.entity.TaskStatus;
import lombok.Getter;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Getter
public class TaskResponse {

    private final Long id;
    private final String title;
    private final String description;
    private final TaskStatus status;
    private final TaskPriority priority;
    private final LocalDate startDate;
    private final LocalDate endDate;
    private final Integer progress;
    private final Long projectId;
    private final String projectName;
    private final AssigneeDto assignee;
    private final SprintDto sprint;
    private final PhaseDto phase;
    private final LocalDateTime createdAt;

    public TaskResponse(Task task) {
        this.id = task.getId();
        this.title = task.getTitle();
        this.description = task.getDescription();
        this.status = task.getStatus();
        this.priority = task.getPriority();
        this.startDate = task.getStartDate();
        this.endDate = task.getEndDate();
        this.progress = task.getProgress();
        this.projectId = task.getProject().getId();
        this.projectName = task.getProject().getTitle();
        this.assignee = task.getAssignee() != null ? new AssigneeDto(task.getAssignee()) : null;
        this.sprint = task.getSprint() != null ? new SprintDto(task.getSprint()) : null;
        this.phase = task.getPhase() != null ? new PhaseDto(task.getPhase()) : null;
        this.createdAt = task.getCreatedAt();
    }

    @Getter
    public static class AssigneeDto {
        private final Long id;
        private final String email;
        private final String nickname;

        public AssigneeDto(kr.ai.lineosft.projectmanagement.domain.member.entity.Member member) {
            this.id = member.getId();
            this.email = member.getEmail();
            this.nickname = member.getNickname();
        }
    }

    @Getter
    public static class SprintDto {
        private final Long id;
        private final String name;

        public SprintDto(kr.ai.lineosft.projectmanagement.domain.project.entity.Sprint sprint) {
            this.id = sprint.getId();
            this.name = sprint.getName();
        }
    }

    @Getter
    public static class PhaseDto {
        private final Long id;
        private final String name;

        public PhaseDto(kr.ai.lineosft.projectmanagement.domain.project.entity.Phase phase) {
            this.id = phase.getId();
            this.name = phase.getName();
        }
    }
}
