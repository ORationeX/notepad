package kr.ai.lineosft.projectmanagement.api.project.dto;

import kr.ai.lineosft.projectmanagement.domain.project.entity.TaskHistory;
import kr.ai.lineosft.projectmanagement.domain.project.entity.TaskStatus;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class TaskHistoryResponse {

    private final Long id;
    private final TaskStatus fromStatus;
    private final TaskStatus toStatus;
    private final String modifierNickname;
    private final LocalDateTime modifiedAt;
    private final String comment;

    public TaskHistoryResponse(TaskHistory history) {
        this.id = history.getId();
        this.fromStatus = history.getFromStatus();
        this.toStatus = history.getToStatus();
        this.modifierNickname = history.getModifier() != null ? history.getModifier().getNickname() : "시스템";
        this.modifiedAt = history.getModifiedAt();
        this.comment = history.getComment();
    }
}
