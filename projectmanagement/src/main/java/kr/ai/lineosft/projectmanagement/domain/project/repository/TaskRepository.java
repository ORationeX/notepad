package kr.ai.lineosft.projectmanagement.domain.project.repository;

import kr.ai.lineosft.projectmanagement.domain.project.entity.Task;
import kr.ai.lineosft.projectmanagement.domain.project.entity.TaskStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface TaskRepository extends JpaRepository<Task, Long> {
    @Query("SELECT t FROM Task t LEFT JOIN FETCH t.assignee LEFT JOIN FETCH t.sprint LEFT JOIN FETCH t.phase LEFT JOIN FETCH t.requirement WHERE t.project.id = :projectId ORDER BY t.createdAt DESC")
    List<Task> findByProjectIdWithRelations(@Param("projectId") Long projectId);

    @Query("SELECT t FROM Task t JOIN FETCH t.project LEFT JOIN FETCH t.assignee LEFT JOIN FETCH t.sprint LEFT JOIN FETCH t.phase LEFT JOIN FETCH t.requirement ORDER BY t.startDate ASC, t.createdAt DESC")
    List<Task> findAllWithRelations();

    @Query("SELECT t FROM Task t LEFT JOIN FETCH t.assignee WHERE t.requirement.id = :requirementId ORDER BY t.createdAt DESC")
    List<Task> findByRequirementId(@Param("requirementId") Long requirementId);

    long countByStatus(TaskStatus status);
}
