package kr.ai.lineosft.projectmanagement.domain.project.repository;

import kr.ai.lineosft.projectmanagement.domain.project.entity.TaskHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface TaskHistoryRepository extends JpaRepository<TaskHistory, Long> {
    @Query("SELECT th FROM TaskHistory th LEFT JOIN FETCH th.modifier WHERE th.task.id = :taskId ORDER BY th.modifiedAt DESC")
    List<TaskHistory> findByTaskIdWithRelations(@Param("taskId") Long taskId);
}
    